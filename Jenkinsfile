pipeline {
    agent any

    environment {
        DEMO_SECRET = credentials('employeeleave-demo-secret')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                bat '"C:\\Users\\admin\\AppData\\Local\\Programs\\Python\\Python311\\python.exe" -m pip install -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                bat '"C:\\Users\\admin\\AppData\\Local\\Programs\\Python\\Python311\\python.exe" -m pytest'
            }
        }

        stage('Credentials Check') {
            steps {
                echo 'Jenkins secret loaded successfully'
            }
        }
    }
}