pipeline {
    agent any

    tools {
        maven 'maven'
        jdk 'java-17'
    }

    environment {
        IMAGE_NAME         = "kunu12345/devsecops-ai-powered:${GIT_COMMIT}"
        AKS_CLUSTER_NAME   = "quantam-aks"
        AKS_RESOURCE_GROUP = "quantam-rg"
    }

    stages {

        stage('Git Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/Krunal-Dharme/DevSecOps-AI-Powered.git'
            }
        }

        stage('Compile') {
            steps {
                sh '''
                    echo "Compiling the code..."
                    mvn compile
                '''
            }
        }

        stage('Build') {
            steps {
                sh '''
                    echo "Building the application..."
                    mvn clean package
                '''
            }
        }

        stage('Docker Build') {
            steps {
                sh '''
                    echo "Building Docker image..."
                    docker build -t ${IMAGE_NAME} .
                '''
            }
        }

        stage('Docker Login') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-creds',
                        usernameVariable: 'DOCKER_USERNAME',
                        passwordVariable: 'DOCKER_PASSWORD'
                    )
                ]) {
                    sh '''
                        echo "Logging into Docker Hub..."
                        echo $DOCKER_PASSWORD | docker login -u $DOCKER_USERNAME --password-stdin
                    '''
                }
            }
        }

        stage('Docker Push') {
            steps {
                sh '''
                    echo "Pushing Docker image..."
                    docker push ${IMAGE_NAME}
                '''
            }
        }

        stage('Azure Login') {
            steps {
                withCredentials([
                    string(credentialsId: 'ARM_CLIENT_ID', variable: 'ARM_CLIENT_ID'),
                    string(credentialsId: 'ARM_CLIENT_SECRET', variable: 'ARM_CLIENT_SECRET'),
                    string(credentialsId: 'ARM_TENANT_ID', variable: 'ARM_TENANT_ID'),
                    string(credentialsId: 'ARM_SUBSCRIPTION_ID', variable: 'ARM_SUBSCRIPTION_ID')
                ]) {
                    sh '''
                        echo "Logging into Azure..."

                        az login --service-principal \
                          --username $ARM_CLIENT_ID \
                          --password $ARM_CLIENT_SECRET \
                          --tenant $ARM_TENANT_ID

                        az account set --subscription $ARM_SUBSCRIPTION_ID
                    '''
                }
            }
        }

        stage('Update Kubeconfig') {
            steps {
                sh '''
                    echo "Updating AKS kubeconfig..."

                    az aks get-credentials \
                      --resource-group ${AKS_RESOURCE_GROUP} \
                      --name ${AKS_CLUSTER_NAME} \
                      --overwrite-existing
                '''
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                withKubeConfig(
                    clusterName: 'quantam-aks',
                    credentialsId: 'kube',
                    namespace: 'quantam',
                    serverUrl: 'https://quantamaks-c4eef10z.hcp.centralindia.azmk8s.io',
                    restrictKubeConfigAccess: false
                ) {
                    sh '''
                        echo "Deploying to Kubernetes..."

                        kubectl apply -f deployment.yaml -n quantam
                    '''
                }
            }
        }
    }
}
