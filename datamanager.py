import numpy as np
import inspect
import scipy.optimize as sopt

import warnings

class DataManager():
	def __init__(self):
		self.data = None;
		# self.mask = None
		self.fit = None;
		self.dataIsValid = False;
		self.fitfuncIsValid = False;
		self.__observers = []
		self.__fitfunc = None;
		self.__fitfuncString = None;
		self.fitfuncVariables = {}
		self.fitfuncArgs = None;

	def attach(self,func):
		self.__observers.append(func)

	def detach(self,func):
		self.__observers.remove(func)

	# Right now the name argument lets observers tell what notification was issued. Another option would be to have the class keep a state variable that says its current state.
	# The notification/string idea is probably more extensible though.
	def notify(self,name=None):
		for func in self.__observers:
			func(self,name)

	def performFit(self):
		self.notify("FitStarted")
		print("=== NEW FIT ===")
		print("Fitting with model equation: {0}".format(self.__fitfuncString))
		try:
			initGuess = [self.fitfuncVariables[k][0] for k in self.fitfuncVariables['args']][1:] # Pulls the initial guess out of the variable parameters
			lBounds = [self.fitfuncVariables[k][1] for k in self.fitfuncVariables['args']]
			uBounds = [self.fitfuncVariables[k][2] for k in self.fitfuncVariables['args']]
			bnds = (lBounds[1:],uBounds[1:])
			popt,pcov = sopt.curve_fit(self.__fitfunc,self.data[~self.data.mask[:,0],0].data,self.data[~self.data.mask[:,1],1].data,p0=initGuess,bounds=(bnds))
		except Exception as e:
			print("Something went wrong")
			print(e)
			return
		print("Fit succeeded.")
		print("popt = {0}".format(popt))
		print("pcov = {0}".format(pcov))
		for i in range(1,self.fitfuncVariables['nargs']):
			v = self.fitfuncVariables['args'][i]
			oldParams = self.fitfuncVariables[v]
			confidence = 1.96*np.sqrt(pcov[i-1,i-1])
			optvar = popt[i-1]
			self.fitfuncVariables[v] = np.concatenate([oldParams[0:3],[optvar,optvar-confidence,optvar+confidence]])
		splitFit = self.__fitfuncString.split(":")
		splitVars = splitFit[0].split(",") # 0-th element will be up to the first (x) variable. Rest will be the replacement variables
		print("Fit Results\n\tvarName: value [95% confidence]")
		for i in range(0,len(popt)):
			varChar = splitVars[i+1].strip()
			confidence = 1.96*np.sqrt(pcov[i,i]);
			print("\t{:s}: {:2.3e} [{:2.3e},{:2.3e}]".format(varChar,popt[i],popt[i]-confidence,popt[i]+confidence))
		fitX = np.linspace(np.amin(self.data[:,0]),np.amax(self.data[:,0]),100)
		fitY = self.__fitfunc(fitX,*popt)
		if (fitY.shape == ()): # This is to catch the case where the independent variable wasn't in the expression which causes the lambda function to just spit out a constant.
			fitY = np.repeat(self.__fitfunc(fitX,*popt),len(fitX))
		self.fit = np.column_stack((fitX,fitY));
		self.notify("FitFinished")

	def setFitFunc(self,fitFuncAsString):
		try:
			func=eval(fitFuncAsString) # This will see if the function is even valid python
			args = inspect.getfullargspec(func).args # Try to extract the function signature, argument names, and number of arguments
			nargs = len(args)
			# Generate some fake data.
			randX = np.random.random((10))
			randY = np.random.random((10))
			# Temporarily disable the optimizer warning because we know the function probably won't fit. We just want to know if it can be called.
			warnings.simplefilter('ignore', sopt.OptimizeWarning)
			sopt.curve_fit(func,randX,randY) # We're just going to try to call the curve fitter with some random data, which should show whether the fit function is acceptable.
			warnings.simplefilter('always', sopt.OptimizeWarning)
		except Exception as e:
			self.fitfuncIsValid = False;
			self.notify();
			return;
		self.__fitfuncString = fitFuncAsString;
		self.__fitfunc = eval(fitFuncAsString);
		# Construct a new dictionary using the new argument names. This has the advantage of preserving any variables that were already defined
		# while removing any that were deleted from the function definition
		newArgsDict = {};
		for a in args:
			if (a in self.fitfuncVariables):
				newArgsDict[a] = self.fitfuncVariables[a]
			else:
				newArgsDict[a] = [1,-np.inf,np.inf,np.nan,np.nan,np.nan]
		self.fitfuncVariables = newArgsDict;
		self.fitfuncVariables['args'] = args;
		self.fitfuncVariables['nargs'] = len(args)
		self.fitfuncIsValid = True;
		self.notify("FitFuncChanged")
		if (self.dataIsValid is True):
			self.performFit();

	def setData(self,data):
		if (data is not None):
			self.data = np.ma.array(data,mask=np.zeros((data.shape)))
			self.dataIsValid = True;
			if (self.fitfuncIsValid):
				self.performFit()
		else:
			self.data = None;
			self.dataIsValid = False;
		self.notify();

	def updateParams(self,var,vals):
		print("Updating")
		oldVars = self.fitfuncVariables[var]
		self.fitfuncVariables[var] = np.concatenate((vals,oldVars[3:]))
		if (self.fitfuncIsValid and self.dataIsValid):
			self.performFit()
		self.notify("ParamsUpdated");
		# print(self.fitfuncVariables[var][pos])
		# self.fitfuncVariables[var][pos] = newVal;

	def updateMask(self,newMask,setMasked):
		if (setMasked == True):
			self.data.mask[newMask] = True
		else:
			self.data.mask[newMask] = False
		if (self.dataIsValid is True and self.fitfuncIsValid is True):
			self.performFit();
		self.notify("MaskUpdated")
