pipeline {
    agent any

    environment {
        MONGODB_URI = 'mongodb://localhost:27017/thinkboard_mod_tut'
        BACKEND_PORT = '5001'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Node.js') {
            steps {
                sh 'node --version'
                sh 'cd backend && npm install'
            }
        }

        stage('Start Backend') {
            steps {
                sh '''
                    cd backend
                    nohup npm run dev > /tmp/backend.log 2>&1 &
                    echo "Backend PID: $!"
                    sleep 5
                '''
            }
        }

        stage('Wait for Backend') {
            steps {
                sh '''
                    timeout 30 bash -c \'until curl -s http://localhost:5001/api/notes > /dev/null; do sleep 2; done\'
                    echo "Backend is ready"
                '''
            }
        }

        stage('Setup Python') {
            steps {
                sh 'python3 --version'
                sh 'cd tests && pip install -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    cd tests
                    pytest testcases/ -v --alluredir=reports/allure-results --clean-alluredir
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'tests/reports/allure-results/**', allowEmptyArchive: true
                }
            }
        }

        stage('Generate Allure Report') {
            steps {
                sh '''
                    cd tests
                    allure generate reports/allure-results -o reports/allure-report --clean
                '''
            }
            post {
                always {
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'tests/reports/allure-report',
                        reportFiles: 'index.html',
                        reportName: 'Allure Report'
                    ])
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }
        success {
            echo 'Tests passed!'
        }
        failure {
            echo 'Tests failed!'
        }
    }
}
