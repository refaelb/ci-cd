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
def ci (reg, tag, repo, branch, imageName):
    system('git clone '+repo)
    chdir(imageName)
    system('pwd')
    # system('git checkout dev')
    folderName(reg, tag, repo, branch, imageName)

####loop folder####
def folderName(reg, tag, repo, branch, imageName):
  p=os.listdir()
  for i in p:
    # print(i)
    if os.path.isdir(i):
        print(i)
        build(reg, tag, repo, branch, imageName,i)

####build####
def build (reg, tag, repo, branch, imageName,i):
  p=os.listdir()
  if 'Dockerfile' in p:
    chdir(i)
    print(imageName)
    system('docker build -t '+reg+':'+i+"."+tag+' .')
    system('docker push '+reg+':'+i+'.'+tag)
    chdir('./..')
    deployment(imageName, data, namespace, dataService, chartName, host,i)
  else:
    chdir('./..')


####configmap####
def createConfigmap(imageName, namespace,i):
    configmap="""
    apiVersion: v1
    kind: ConfigMap
    metadata:
        name: {}ConfigMap
        namespace: {}
    data:
        master: refael """.format(i, namespace, )
    chdir('home_dir/'+i)
    with open(i+'-configmap.yaml', 'w+' ) as file:
        docs = yaml.load(configmap,  Loader=yaml.FullLoader)
        yaml.dump(docs, file, sort_keys=False)
        chdir('../../')
        system('pwd')
        system('ls')
        for env in open(imageName+'/'+i+'/'+i+".env","r+").readlines():
            file = open("./home_dir/"+i+"/"+i+"-configmap.yaml","a+")
            tab = "  "
            file.write(str(tab+env))
    system('pwd')
    chdir('./home_dir/'+i)
    system('kubectl create configmap {} --from-file={}-configmap.yaml -n {}' .format(i, i, namespace))
    system('kubectl apply -f {}-configmap.yaml -n {}'.format( i, namespace))

####deployment####
def deployment (imageName, data, namespace, dataService, chartName, host,i):
    ingres=False
    # system('pwd')
    # for env in open(i+".env","r+").readlines():
    #     if "ingres" in env :
    #         ingres=True
    #         print(env)
    #         break

    Path("./../home_dir").mkdir(parents=True, exist_ok=True)
    chdir("./../home_dir")
    system("helm create "+i )
    confFile = i+"-configmap"
    file = open(i+"/values.yaml","w+")
    docs = yaml.load(data.format(i, confFile),  Loader=yaml.FullLoader)
    yaml.dump(docs, file, sort_keys=False)
    chdir("../")

    # createConfigmap(imageName, namespace,i)

    file = open("values.yaml","a+")
    docs = yaml.load(dataService.format("","","","",ingres,host,"","",""),  Loader=yaml.FullLoader)
    yaml.dump(docs, file,sort_keys=False)
    file.close()
    chdir("../")
    # system("helm upgrade {} {}  -n {} ".format(chartName, imageName, namespace))



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
repo = ('https://github.com/MomentumTeam/SuperNova.git')
tag = ('0.0.1')
reg = ('refael058325/ci')
branch = ('main')


a = repo.rsplit('.',1)[0]
imageName = a.rsplit('/',3)[3]
print(imageName)



# schedule.every().day.at("15:44").do(ci(reg, tag, repo, branch,imageName))

# while True:
#     schedule.run_pending()
#     time.sleep(60) # wait one minute


ci(reg, tag, repo, branch,imageName)