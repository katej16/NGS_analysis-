#!/bin/python

import os
import sys
import csv
import glob 
import time
import gzip
import fnmatch
import logging
import argparse
import subprocess
import urllib.request

# Example Command: 
# python3 autotrim.py --trimmomatic "-phred33 -threads 8 ILLUMINACLIP:adapters.fa:2:30:10 LEADING:3 TRAILING:3 SLIDINGWINDOW:4:15 MINLEN:75" ----fastqc TRUE


#Create log file
logging.basicConfig(filename='trimmomatic.log',level=logging.DEBUG, format='%(asctime)s %(message)s')


#List all R1 fastq files in the current folder 
r1_fastqs = fnmatch.filter(os.listdir(), '*_R1*')
r1_fastqs.sort()
r2_fastqs = fnmatch.filter(os.listdir(), '*_R2*')
r2_fastqs.sort()

logging.info(r1_fastqs)
logging.info(r2_fastqs)
#This script was entire written by Vikas Peddu and edited by Quynh Phung in the Greninger lab at the UW  

#Parse arguments 
parser = argparse.ArgumentParser(description = "input trimmomatic flags")
parser.add_argument("--paired", dest = 'paired', type = bool, help = "Option for paired end reads")
parser.add_argument("--spades", dest = 'spades' ,type=bool,  help = "Input all flags after SPADES.py enclosed in double quotes here")
parser.add_argument("--trimmomatic", dest='trimmomatic',nargs = '?' ,type=str, 
	help="Input flags after 'trimmomatic PE' enclosed in double quotes \
	excluding the filenames. Adapter file must be named adapters.fa. This will \
	automatically download from github")
parser.add_argument("--kallisto", dest = 'kallisto',type = str, help = "Input all flags after 'kallisto_quant' enclosed in double quotes here \
	IMPORTANT: if single end you must supply -l and -s arguments for kallisto here- the pipeline will break if you do not")
parser.add_argument("--debrowser", dest = 'debrowser', type = bool, help = "Takes kallisto output and rewrites as debrowser ready input file")
parser.add_argument("--fastqc", dest = 'fastqc', type = bool, help = "Runs fastqc on all trimmed files")

args = parser.parse_args()


#Run Trimmomatic
if(args.trimmomatic):
	#download adapters.fa from github
	url = "https://github.com/katej16/NGS_analysis-/blob/main/Concatenated.fa"
	filename, headers = urllib.request.urlretrieve(url, filename="adapters.fa")
	trimmed_read_count = []
	trimmed_read_count.append('Trimmed read count')
	print('Running Trimmomatic with arguments: ' + args.trimmomatic)
	for fq in range(len(r1_fastqs)): 
		fq_name = (r1_fastqs[fq].split('_R')[0])
		print('Trimming ' + fq_name)
		trim_r1_name = 'trimmed.' + r1_fastqs[fq]
		if(args.paired):
			trim_r2_name = 'trimmed.' + r2_fastqs[fq]
			trimmomatic_cmd = 'trimmomatic PE ' + ' ' + r1_fastqs[fq] + ' ' + r2_fastqs[fq] + ' ' + trim_r1_name + ' /dev/null/ ' + trim_r2_name + ' /dev/null/ ' + args.trimmomatic
		else:
			trimmomatic_cmd = 'trimmomatic SE ' + ' ' + r1_fastqs[fq] + ' ' + trim_r1_name  + ' ' + args.trimmomatic
		subprocess.call(trimmomatic_cmd, shell = True, stderr = subprocess.DEVNULL, stdout = subprocess.DEVNULL)
		logging.info(trimmomatic_cmd)
	#Redefining fastq list so everything below works off of the trimmed files 
	trimmed_files = fnmatch.filter(os.listdir(), 'trimmed.*')
	r1_fastqs = fnmatch.filter(trimmed_files, '*R1*')
	r2_fastqs = fnmatch.filter(trimmed_files, '*R2*')


#Runs FASTQC
if args.fastqc:
	print('Running FASTQC') 
	subprocess.call('FASTQC *R1*', shell = True, stderr = subprocess.DEVNULL, stdout = subprocess.DEVNULL)
	subprocess.call('mkdir fastqc_files', shell = True)
	subprocess.call('mv *fastqc* fastqc_files', shell = True, stderr = subprocess.DEVNULL, stdout = subprocess.DEVNULL)
