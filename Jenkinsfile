pipeline {
    agent any

    tools {
        maven 'maven'
        jdk 'java-17'
    }

    environment {
        IMAGE_NAME = "kunu12345/devsecops-ai-powered-new:${GIT_COMMIT}"

        GCP_PROJECT = "project-052ab01a-3589-4f07-a43"
        GKE_CLUSTER = "quantam-gke"
        GKE_ZONE    = "asia-south1-a"
    }

    stages {

        stage('Git Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/Krunal-Dharme/DevSecOps-AI-Powered-GCP.git'
            }
        }

        stage('Compile') {
            steps {
                sh 'mvn compile'
            }
        }

        stage('Build') {
            steps {
                sh 'mvn clean package'
            }
        }

        stage('Docker Build') {
            steps {
                sh 'docker build -t ${IMAGE_NAME} .'
            }
        }

        stage('Docker Login') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKER_USERNAME',
                    passwordVariable: 'DOCKER_PASSWORD'
                )]) {
                    sh '''
                        echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
                    '''
                }
            }
        }

        stage('Docker Push') {
            steps {
                sh 'docker push ${IMAGE_NAME}'
            }
        }

        stage('Configure GCP Project') {
            steps {
                sh '''
                    gcloud config set project ${GCP_PROJECT}
                '''
            }
        }

        stage('Get GKE Credentials') {
            steps {
                sh '''
                    export USE_GKE_GCLOUD_AUTH_PLUGIN=True

                    gcloud container clusters get-credentials ${GKE_CLUSTER} \
                        --zone ${GKE_ZONE} \
                        --project ${GCP_PROJECT}
                '''
            }
        }

        stage('Deploy to GKE') {
            steps {
                sh '''
                    echo "Deploying to Kubernetes..."

                    kubectl apply -f deployment.yaml
                '''
            }
        }
    }
}
