from panda3d.core import *
from direct.showbase import DConfig
import string

try:
    language = config.GetString('language', 'english')
    checkLanguage = config.GetBool('check-language', 0)
except NameError:
    # __builtin__.config not defined yet.
    language = DConfig.GetString('language', 'english')
    checkLanguage = DConfig.GetBool('check-language', 0)

def getLanguage():
    return language


print('OTPLocalizer: Running in language: %s' % language)
if language == 'english':
    _languageModule = 'otp.otpbase.OTPLocalizer' + language.capitalize()
else:
    checkLanguage = 1
    _languageModule = 'otp.otpbase.OTPLocalizer_' + language.capitalize()
print('from ' + _languageModule + ' import *')
from otp.otpbase.OTPLocalizerEnglish import *
if language == 'french':
    from otp.otpbase.OTPLocalizer_French import *
elif language == 'polish':
    from otp.otpbase.OTPLocalizer_Polish import *
elif language == 'german':
    from otp.otpbase.OTPLocalizer_German import *
if checkLanguage:
    l = {}
    g = {}
    englishModule = __import__('otp.otpbase.OTPLocalizerEnglish', g, l)
    foreignModule = __import__(_languageModule, g, l)
    for key, val in englishModule.__dict__.items():
        if key not in foreignModule.__dict__:
            print('WARNING: Foreign module: %s missing key: %s' % (_languageModule, key))
            locals()[key] = val
        elif isinstance(val, dict):
            fval = foreignModule.__dict__.get(key)
            for dkey, dval in val.items():
                if dkey not in fval:
                    print('WARNING: Foreign module: %s missing key: %s.%s' % (_languageModule, key, dkey))
                    fval[dkey] = dval

            for dkey in fval.keys():
                if dkey not in val:
                    print('WARNING: Foreign module: %s extra key: %s.%s' % (_languageModule, key, dkey))

    for key in foreignModule.__dict__.keys():
        if key not in englishModule.__dict__:
            print('WARNING: Foreign module: %s extra key: %s' % (_languageModule, key))
