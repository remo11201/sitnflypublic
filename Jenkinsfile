/*pipeline {
    agent any

    stages {
        stage('Checkout SCM') {
            steps {
                checkout scm
            }
        }
        stage('Setup Python Environment') {
            steps {
                sh 'python3 -m venv venv'
                sh '. venv/bin/activate && pip install -r requirements.txt'
            }
        }
        stage('Test') {
            steps {
                sh '''
                . venv/bin/activate
                pytest --junitxml=reports/test-results.xml --cov=app --cov-report=xml:reports/coverage.xml
                '''
            }
            post {
                always {
                    junit 'reports/test-results.xml'
                    publishCoverage adapters: [jacocoAdapter('reports/coverage.xml')]
                }
            }
        }
        stage('OWASP DependencyCheck') {
            steps {
                sh '''
                echo 'Unable to update from NVD. No connection'
                # dependency-check --project "SSD-Group16" --scan /app --out reports/ --format XML --noupdate
                '''
            }
            post {
                always {
                    dependencyCheckPublisher pattern: 'reports/dependency-check-report.xml'
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }
        success {
            echo 'Build and Test succeeded!'
        }
        failure {
            echo 'Build or Test failed.'
        }
    }
}*/

pipeline {
    agent any
    stages {
        stage ('Checkout') {
            steps {
                git branch:'main', url: 'https://github.com/afiqdanialll/sitnflypublic.git'
            }
        }

        stage('Code Quality Check via SonarQube') {
            steps {
                script {
                def scannerHome = tool 'SonarQube';
                    withSonarQubeEnv('SonarQube') {
                    sh "/var/jenkins_home/tools/hudson.plugins.sonar.SonarRunnerInstallation/SonarQube/bin/sonar-scanner -Dsonar.projectKey=Sitnfly -Dsonar.sources=. -Dsonar.host.url=http://192.168.86.108:9000 -Dsonar.token=sqp_e8308ae0f5381d2d0d2ab674c2059c25476df7c0"
                    }
                }
            }
        }
    }
    post {
        always {
            recordIssues enabledForFailure: true, tool: sonarQube()
        }
    }
}

