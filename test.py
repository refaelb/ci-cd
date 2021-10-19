import os
import sys
import fileinput
import yaml
namespace = ('demo')
chartName = ('test') 
host = ('test') 
repo = ('https://github.com/MomentumTeam/SuperNova.git')
tag = ('0.0.1')
reg = ('refael058325/ci')
branch = ('main')
ingres = False
workdir='/home/refael/script/ci-cd/src'
imageName = 'SuperNova'
os.chdir(workdir)
os.system('pwd')
configmap="""
apiVersion: v1
kind: ConfigMap
metadata:
    name: {}ConfigMap
    namespace: {}
data:
    master: refael """.format(imageName, namespace, )
os.chdir(workdir+'/home_dir/')
with open(imageName+'-configmap.yaml', 'w+' ) as file:
    docs = yaml.load(configmap,  Loader=yaml.FullLoader)
    yaml.dump(docs, file, sort_keys=False)
for root, dirs, files in os.walk(workdir+'/'+imageName):
    for file in files:
        if file.endswith('.env'):
            print(file)
            os.chdir(workdir+'/'+imageName)
            env = open(file,"r+").read() 
            data = open(workdir+"/home_dir/"+imageName+"-configmap.yaml","a+")
            tab = "  "
            data.write(tab+ str(env))
            
for i, line in enumerate(fileinput.input(workdir+'/home_dir/'+imageName+'-configmap.yaml', inplace=1)):
    sys.stdout.write(line.replace('=', ': '))  