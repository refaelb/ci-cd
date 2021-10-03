from os import read, write, chdir, system 
from pathlib import Path
import yaml
import argparse
import re 
import time
import os



data='''
replicaCount: 1

image:
  repository: {}
  pullPolicy: Always
  # Overrides the image tag whose default is the chart appVersion.
  tag: "latest"

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


####ci####
def ci (reg, tag, repo, branch, imageName,homeDir):
    system('git clone '+repo)
    chdir(homeDir+'/'+imageName)
    system('pwd')
    system('git checkout dev')
    print('ci')
    folderName(reg, tag, repo, branch, imageName,homeDir)

####loop folder####
def folderName(reg, tag, repo, branch, imageName,homeDir):
  p=os.listdir()
  for i in p:
    if os.path.isdir(i):
        print('loop folder')
        build(reg, tag, repo, branch, imageName,i,homeDir)

####build####
def build (reg, tag, repo, branch, imageName,i,homeDir):
  system('ls')
  chdir(i)
  system('docker build -t '+i+':'+tag+' .')
  system('docker push '+i+':'+tag)
  print ('build')
  deployment(imageName, data, namespace, dataService, chartName, host,i,homeDir)

   

####configmap####
def createConfigmap(imageName, namespace,i,homeDir):
    configmap="""
    apiVersion: v1
    kind: ConfigMap
    metadata:
        name: {}ConfigMap
        namespace: {}
    data:
        master: refael """.format(i, namespace, )
    chdir(homeDir+'/home_dir/'+i)
    system('pwd')
    system('ls')
    with open(i+'-configmap.yaml', 'w+' ) as file:
        docs = yaml.load(configmap,  Loader=yaml.FullLoader)
        yaml.dump(docs, file, sort_keys=False)
        chdir(homeDir+'/'+imageName+'/'+i)
        system('pwd')
        system('ls')
        for env in open(i+".env","r+").readlines():
            file = open(homeDir+"/home_dir/"+i+"/"+i+"-configmap.yaml","a+")
            tab = "  "
            file.write(str(tab+env))
    system('pwd')
    chdir(homeDir+'/home_dir/'+i)
    system('kubectl create configmap {} --from-file={}-configmap.yaml -n {}' .format(i, i, namespace))

####deployment####
def deployment (imageName, data, namespace, dataService, chartName, host,i,homeDir):
    ingres=False
    system('pwd')
    for env in open(i+".env","r+").readlines():
        if "ingres" in env :
            ingres=True
            print(env)
            break

    Path(homeDir).mkdir(parents=True, exist_ok=True)
    chdir(homeDir+"/home_dir")
    system("pwd")
    system("helm create "+i )
    confFile = i+"-configmap"
    file = open(i+"/values.yaml","w+")
    docs = yaml.load(data.format(i, confFile),  Loader=yaml.FullLoader)
    yaml.dump(docs, file, sort_keys=False)
    chdir(homeDir)

    createConfigmap(imageName, namespace,i,homeDir)

    file = open(homeDir+'/home_dir/'+i+"/values.yaml","a+")
    docs = yaml.load(dataService.format("","","","",ingres,host,"","",""),  Loader=yaml.FullLoader)
    yaml.dump(docs, file,sort_keys=False)
    file.close()
    chdir(homeDir+'/home_dir/'+i)
    system("helm upgrade {} {}  -n {} ".format(chartName, imageName, namespace))



# parser = argparse.ArgumentParser(description='Personal information')
# parser.add_argument('-repo', dest='repo', type=str, help='repo')
# parser.add_argument('-v', dest='version', type=str, help='version')
# parser.add_argument('-r', dest='registry', type=str, help='registry')
# parser.add_argument('-b', dest='branch', type=str, help='branch')

# parser.add_argument('-n', dest='namespace', type=str, help='namespace')
# parser.add_argument('-c', dest='chartName', type=str, help='chart name')
# parser.add_argument('-ho', dest='host', type=str, help='host name')


# args = parser.parse_args()
# namespace = (args.namespace)
# chartName = (args.chartName)
# host = (args.host)

# repo = (args.repo)
# tag = (args.version)
# reg = (args.registry)
# branch = (args.branch)

namespace = ('demo')
chartName = ('test') 
host = ('test') 
repo = ('https://github.com/refaelb/image_project.git')
tag = ('0.01')
reg = ('refael058325/ci')
branch = ('dev')
homeDir = ('/home/refael/script/ci-cd/src')


a = repo.rsplit('.',1)[0]
imageName = a.rsplit('/',3)[3]
ci(reg, tag, repo, branch,imageName,homeDir)



# schedule.every().day.at("15:44").do(ci(reg, tag, repo, branch,imageName))

# while True:
#     schedule.run_pending()
#     time.sleep(60) # wait one minute

