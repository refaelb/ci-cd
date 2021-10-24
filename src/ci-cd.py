from os import read, write, chdir, system 
from pathlib import Path
import yaml
import argparse
import re 
# import schedule
import time
import os



data='''
replicaCount: 1

image:
  repository: {}
  pullPolicy: Always
  # Overrides the image tag whose default is the chart appVersion.
  tag: {}.{}

imagePullSecrets: []
nameOverride: ""
fullnameOverride: ""
configmap: {}
'''
dataService = """
  serviceAccount:
    # Specifies whether a service account should be created
    create: true
    # Annotations to add to the service account
    annotations: {}
    # The name of the service account to use.
    # If not set and create is true, a name is generated using the fullname template
    name: ""

  podAnnotations: {}

  podSecurityContext: {}
    # fsGroup: 2000

  securityContext: {}
    # capabilities:
    #   drop:
    #   - ALL
    # readOnlyRootFilesystem: true
    # runAsNonRoot: true
    # runAsUser: 1000

  service:
    type: ClusterIP
    port: 3000

  ingress:
    enabled: {}
    annotations: 
      kubernetes.io/ingress.class: addon-http-application-routing
      # kubernetes.io/ingress.class: nginx
      # kubernetes.io/tls-acme: "true"
    hosts:
      - host: {}
        paths:
        - path: /
          pathType: ImplementationSpecific
          backend:
            serviceName: chart-example.local
            servicePort: 3000
    tls: []
    #  - secretName: chart-example-tls
    #    hosts:
    #      - chart-example.local

  resources: {}
    # We usually recommend not to specify default resources and to leave this as a conscious
    # choice for the user. This also increases chances charts run on environments with little
    # resources, such as Minikube. If you do want to specify resources, uncomment the following
    # lines, adjust them as necessary, and remove the curly braces after 'resources:'.
    # limits:
    #   cpu: 100m
    #   memory: 128Mi
    # requests:
    #   cpu: 100m
    #   memory: 128Mi

  autoscaling:
    enabled: false
    minReplicas: 1
    maxReplicas: 100
    targetCPUUtilizationPercentage: 80
    # targetMemoryUtilizationPercentage: 80

  nodeSelector: {}

  tolerations: []

  affinity: {}

"""

####varabels####
namespace = ('demo')
chartName = ('test') 
host = ('test') 
repo = ('https://github.com/MomentumTeam/SuperNova.git')
tag = ('0.0.1')
reg = ('refael058325/ci')
branch = ('main')
ingres = False
workdir='/home/refael/script/ci-cd/src'

a = repo.rsplit('.',1)[0]
imageName = a.rsplit('/',3)[3]

####ci####
system('git clone '+repo)
chdir(imageName)
system('git checkout '+branch)

####loop folder####
p=os.listdir()
for i in p:
    if os.path.isdir(i): 
        chdir(i)
        p=os.listdir()
        if 'Dockerfile' in (p):
            system('docker build -t '+reg+':'+i+"."+tag+' .')
            system('docker push '+reg+':'+i+'.'+tag)
            ###deploy###
            Path(workdir+"/home_dir").mkdir(parents=True, exist_ok=True)
            chdir(workdir+"/home_dir")
            system("helm create "+i )
            confFile = i+"-configmap"
            file = open(i+"/values.yaml","w+")
            docs = yaml.load(data.format(reg, i, tag, confFile),  Loader=yaml.FullLoader)
            yaml.dump(docs, file, sort_keys=False)
            # chdir("../")
            file = open(i+"/values.yaml","a+")
            docs = yaml.load(dataService.format("","","","",ingres,host,"","",""),  Loader=yaml.FullLoader)
            yaml.dump(docs, file,sort_keys=False)
            file.close()
            chdir("../")
            # system("helm upgrade {} {}  -n {} ".format(chartName, imageName, namespace))
            chdir(workdir+'/'+imageName)
        else:
            chdir('./..')
               

####configmap####
# def createConfigmap(imageName, namespace,i):
configmap="""
apiVersion: v1
kind: ConfigMap
metadata:
    name: {}ConfigMap
    namespace: {}
data:
    master: refael """.format(imageName, namespace, )
chdir(workdir+'/home_dir/')
with open(imageName+'-configmap.yaml', 'w+' ) as file:
    docs = yaml.load(configmap,  Loader=yaml.FullLoader)
    yaml.dump(docs, file, sort_keys=False)
    # chdir(workdir+'/home_dir')
    with open(imageName+'/'+imageName+".env","r+").readlines() as env:
        file = open(workdir+"/home_dir/"+imageName+"-configmap.yaml","a+")
        tab = "  "
        file.write(str(tab+env))
system('pwd')
# chdir('./home_dir/')
system('kubectl create configmap {} --from-file={}-configmap.yaml -n {}' .format(i, i, namespace))
system('kubectl apply -f {}-configmap.yaml -n {}'.format( i, namespace))
