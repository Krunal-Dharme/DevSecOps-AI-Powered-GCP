pipeline {

    agent any

    tools {
        jdk   'java-17'
        maven 'maven'
    }

    environment {

        /* ---------------- Docker ---------------- */
        IMAGE_NAME = "kunu12345/devsecops-ai-powered-new:${GIT_COMMIT}"

        /* ---------------- GCP / GKE ---------------- */
        GCP_PROJECT = "project-052ab01a-3589-4f07-a43"
        GKE_CLUSTER = "quantam-gke"
        GKE_ZONE    = "asia-south1-a"
        NAMESPACE   = "default"

        /* ---------------- AI (OLLAMA ONLY) ---------------- */
        OLLAMA_HOST  = "http://127.0.0.1:11434"
        OLLAMA_MODEL = "mistral:7b"

        AI_FAIL_ON_CRITICAL = "false"
    }

    stages {

    /* =====================================================
       SOURCE
    ===================================================== */

        stage('Git Checkout') {
            steps {
                git url: 'https://github.com/Krunal-Dharme/DevSecOps-AI-Powered-GCP.git',
                    branch: 'main'
            }
        }

    /* =====================================================
       BUILD
    ===================================================== */

        stage('Verify Java') {
            steps {
                sh '''
                    java -version
                    javac -version
                    mvn -version
                '''
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

    /* =====================================================
       AI LAYER 1 — Code Review (OLLAMA ONLY)
    ===================================================== */

        stage('Ensure Ollama Model') {
            steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
                    sh '''
                        if ollama list | grep -q "${OLLAMA_MODEL}"; then
                            echo "[AI] Model already available"
                        else
                            echo "[AI] Pulling model..."
                            ollama pull ${OLLAMA_MODEL}
                        fi
                    '''
                }
            }
        }

        stage('AI Code Review') {
            steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
                    sh 'python3 scripts/ai_code_review.py'
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'ai-code-review-report.md', allowEmptyArchive: true
                }
            }
        }

    /* =====================================================
       TEST + COVERAGE
    ===================================================== */

        stage('Test & Coverage') {
            steps {
                sh 'mvn test jacoco:report'
            }

            post {
                always {
                    jacoco(
                        execPattern: 'target/jacoco.exec',
                        classPattern: 'target/classes',
                        sourcePattern: 'src/main/java'
                    )
                }
            }
        }

    /* =====================================================
       STATIC CODE ANALYSIS
    ===================================================== */

        stage('SonarQube Scan') {
            steps {
                withSonarQubeEnv('SonarQube') {
                    sh 'mvn sonar:sonar'
                }
            }
        }

        stage('Quality Gate') {
            steps {
                timeout(time: 10, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

    /* =====================================================
       OWASP DEPENDENCY SCAN
    ===================================================== */

        stage('OWASP Dependency Check') {
            steps {
                sh 'mvn org.owasp:dependency-check-maven:check -Dformat=ALL'
            }
        }

    /* =====================================================
       CONTAINER SECURITY + BUILD
    ===================================================== */

        stage('Container Security & Build') {

            parallel {

                stage('Trivy Scan') {
                    steps {
                        sh 'bash trivy-docker-image-scan.sh'
                    }
                }

                stage('OPA Docker Policy') {
                    steps {
                        sh '''
                        docker run --rm \
                        -v $(pwd):/project \
                        openpolicyagent/conftest \
                        test --policy dockerfile-security.rego Dockerfile
                        '''
                    }
                }

                stage('Docker Build') {
                    steps {
                        sh 'docker build -t ${IMAGE_NAME} .'
                    }
                }
            }
        }

    /* =====================================================
       AI LAYER 2 — Security Analysis (OLLAMA ONLY)
    ===================================================== */

        stage('AI Security Analysis') {
            steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
                    sh 'python3 scripts/ai_security_analysis.py'
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'ai-security-report.md', allowEmptyArchive: true
                }
            }
        }

    /* =====================================================
       DOCKER PUSH
    ===================================================== */

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
                        echo "$DOCKER_PASSWORD" | docker login \
                        -u "$DOCKER_USERNAME" --password-stdin
                    '''
                }
            }
        }

        stage('Docker Push') {
            steps {
                sh 'docker push ${IMAGE_NAME}'
            }
        }

    /* =====================================================
       GKE ACCESS
    ===================================================== */

        stage('Get GKE Credentials') {
            steps {
                sh '''
                    export USE_GKE_GCLOUD_AUTH_PLUGIN=True
                    gcloud config set project ${GCP_PROJECT}
                    gcloud container clusters get-credentials ${GKE_CLUSTER} \
                        --zone ${GKE_ZONE} \
                        --project ${GCP_PROJECT}
                '''
            }
        }

    /* =====================================================
       OPA K8S POLICY
    ===================================================== */

        stage('OPA Kubernetes Policy') {
            steps {
                sh '''
                docker run --rm \
                -v $(pwd):/project \
                openpolicyagent/conftest \
                test --policy opa-k8s-security.rego deployment.yaml
                '''
            }
        }

    /* =====================================================
       AI LAYER 3 — Release Notes (OLLAMA ONLY)
    ===================================================== */

        stage('AI Release Notes') {
            steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
                    sh 'python3 scripts/ai_release_notes.py'
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'ai-release-notes.md', allowEmptyArchive: true
                }
            }
        }

    /* =====================================================
       DEPLOYMENT TO GKE
    ===================================================== */

        stage('Deploy to GKE') {
            steps {
                sh '''
                    sed -i "s|replace|${IMAGE_NAME}|g" deployment.yaml
                    kubectl apply -f deployment.yaml -n ${NAMESPACE}
                '''
            }
        }

    }

    post {

    always {

        echo "====================================================="
        echo "🤖 AI PIPELINE ASSISTANT"
        echo "Open: http://34.93.121.54:5001/"
        echo "====================================================="

        currentBuild.description =
            '<a href="http://34.93.121.54:5001/" target="_blank">🤖 Open AI Pipeline Assistant</a>'
    }

    success {
        echo "✅ Pipeline completed successfully (Ollama AI enabled)"
    }

    unstable {
        echo "⚠️ Pipeline completed with warnings"
    }

    failure {
        echo "❌ Pipeline failed"
    }
}
}
