# -*- coding: utf-8 -*-
"""
Created on Wed Aug  2 07:03:39 2023
PerkinElmer Spectrum IR (FTIR) RTF report parser

@author: markome, kbojanic

Requrements:
python 3.9.16 (developed and tested on) 
pip install striprtf  
"""


from striprtf.striprtf import rtf_to_text 
from pathlib import Path
import pandas as pd
import glob
import datetime




def parseFTRReportFile(fName):

    #with open(fName, 'r') as file: 
    #    rtf_text = file.read() 
    rtf_text = Path(fName).read_text()
    text = rtf_to_text(rtf_text) 
    #print(text)
    
    #flatten the data by removing multiple '|'
    #https://www.geeksforgeeks.org/python-replace-multiple-occurrence-of-character-by-single/
    def replace(string, char):
        return char.join([s for s in string.split(char) if s != ''])
    flatText=replace(text, '|')
    
    #and create tokens that will be used for key/value pair search
    tokens = flatText.split('|')
    tokens=list(filter(lambda a: a != '\n', tokens)) #also remove all '\n'
    #print(tokens)
    
    #parsed keys
    
    #keys=['Report Location', 'Report Creator', 'Report Date', 'Filename', 'Creation Date', 'Analyst', 'Administrator', 'X-Axis Units', 'X-Axis start value', 'X-Axis end value', 'Data interval', 'Number of points',  'Y-Axis Units',  'Description', 'Instrument Model', 'Instrument Serial Number', 'Software Revision', 'Number of Scans',  'Resolution',  'Detector',  'Source',  'Beamsplitter', 'Apodization',  'Spectrum Type', 'Beam Type', 'Phase correction', 'Scan Speed', 'IGram Type', 'Scan Direction',  'Zero Crossings',  'JStop',  'IR-Laser Wavenumber',  'Manufacturer',  'Part Number',  'Serial Number',  'Description', 'ATR Sample base plate', 'Default Scan Range / cm-1',  'Force Applied / N',  'Accessory Type',  'UATR Crystal Combination', 'UATR Number of Bounces',  'UATR Option',  'Manufacturer',  'Part Number',  'Serial Number',  'Description',  'Default Scan Range / cm-1',  'Force Applied / N',  'Accessory Type',  'UATR Crystal Combination',  'UATR Number of Bounces',  'UATR Option']
    
    keys=['Report Location', 'Report Creator', 'Report Date', 'Filename', 'Creation Date', 'Analyst', 'Administrator', 'X-Axis Units', 'X-Axis start value', 'X-Axis end value', 'Data interval', 'Number of points',  'Y-Axis Units',  'Description', 'Instrument Model', 'Instrument Serial Number', 'Software Revision', 'Number of Scans',  'Resolution',  'Detector',  'Source',  'Beamsplitter', 'Apodization',  'Spectrum Type', 'Beam Type', 'Phase correction', 'Scan Speed', 'IGram Type', 'Scan Direction',  'Zero Crossings',  'JStop',  'IR-Laser Wavenumber',  'Manufacturer',  'Part Number',  'Serial Number',  'Description', 'ATR Sample base plate', 'Default Scan Range / cm-1',  'Force Applied / N',  'Accessory Type',  'UATR Crystal Combination', 'UATR Number of Bounces',  'UATR Option',  'Manufacturer',  'Part Number',  'Serial Number',  'Description',  'Default Scan Range / cm-1',  'Force Applied / N',  'Accessory Type',  'UATR Crystal Combination',  'UATR Number of Bounces',  'UATR Option', 'Water Vapor', 'Baseline Low', 'Baseline High', 'Baseline Slope', 'Strong Bands', 'Weak Bands', 'High Noise', 'Vignetting', 'Blocked Beam', 'Negative Bands', 'Zero Transmission', 'Stray Light']
    
    
    #make a list of duplisate key values
    #https://stackoverflow.com/questions/9835762/how-do-i-find-the-duplicates-in-a-list-and-create-another-list-with-them
    seen = set()
    seen_add = seen.add
    # adds all elements it doesn't know yet to seen and all other to seen_twice 
    seen_twice = set( x for x in keys if x in seen or seen_add(x) )
    # turn the set into a list (as requested)
    duplicate_keys = list( seen_twice )
    #print(duplicate_keys)
    
    #define duplication_breaks. prefix will then be used on keys duplicates in final output
    duplication_breaks={}
    duplication_breaks={107: 'Quality_', 66:'Accessory_', 30:'Instrument_', 0:'Sample_'}
    
    
    #keys at the end, not parsed
    remainingKeys =['\nQuality Checks', '\nHistory', 'Who', 'What', 'When', 'Parameters', 'Comment', 'Administrator', 'Created as New Dataset', '24/05/2023 14:42:21', 'Sample 802 By Administrator Date Wednesday, May 24 2023', 'Administrator', 'Atmospheric Correction', '24/05/2023 14:42:21', '\nSpectrum', '\nSummary', 'Sample Name', 'Description', 'Saved or unsaved State', 'Spectrum quality check summary', 'Administrator 802', 'Sample 802 By Administrator Date Wednesday, May 24 2023', 'Saved', 'The Quality Checks do not report any warnings for the sample.']
    
    location = 0
    row_dict={}
    for key in keys:
        prefix=''
        if (tokens.count(key)>0):
            index = tokens.index(key,location) #since there are repeated key values search for key in remaining part of list
            location=index
            value = tokens[index+1]
        else:
            #assuming background
            #print(f'{key} Not found')
            value='N/A'
            prefix='Quality_' #a little dirty hack...
            
        #just create prefix for all keys.
        
        
    
        for db_key in duplication_breaks.keys():
            #print(db_key)
            if location>db_key:
                #print(db_key)
                if (prefix==''): #a little dirty hack comtinued
                    prefix=duplication_breaks[db_key]
                #print(f'DUPLICATE:{prefix}')
                break
        
        storeKey = prefix+key
        row_dict[storeKey]=value
        #print(f'{index}:{storeKey}:{value}')
    return row_dict
 
    
 
    
print('PerkinElmer Spectrum IR (FTIR) RTF report parser')
print('v02 2023_08_02')
print('2do: quality checks')
print('marko.meza@fe.uni-lj.si, krunoslav.bojanic@irb.hr\n')

data = pd.DataFrame()   




#parse all files in folder
reportFolder = './reports/*.rtf'
print(f'Parsing FTR Reports in rtf format from files in folder {reportFolder}')
fileNames=glob.glob(reportFolder)
i=0
for fName in fileNames:
    i=i+1
    print(f'parsing {i} of {len(fileNames)}: {fName}')
    
    row=parseFTRReportFile(fName)
    df = pd.DataFrame([row])
    data = pd.concat([data, df], axis=0)

print('Done.\n')   
nowStr = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
parsedFname = nowStr+'_parsedFRTReports'
print(f'Saving data to {parsedFname}.csv')
data.to_csv(parsedFname+'.csv', index=False)
print(f'Saving data to {parsedFname}.xlsx')
data.to_excel(parsedFname+'.xlsx', index=False)
#print(data)
