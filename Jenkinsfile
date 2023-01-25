// Uses Declarative syntax to run commands inside a container.
pipeline {
    agent {
        kubernetes {
            yamlFile 'python-pod.yaml'
            label 'py-supermgr-build'
            defaultContainer 'py-supermgr-build'
        }
    }
    stages {
        stage('Setup') {
            steps {
                sh """
                pip install --upgrade pip
                pip install .
                """
            }
        }
        stage('Linting') { // Run pylint against your code
            steps {
                script {
                    sh """
                    pylint supermgr/*.py
                    """
                }
            }
        }
    }
    post {
        failure {
            script {
                msg = "Build error for: ${env.JOB_NAME}: ${env.BUILD_NUMBER}: ${env.BUILD_URL}"
                
                //slackSend message: msg, channel: env.SLACK_CHANNEL
                sh "echo ${msg}"
            }
        }
    }
}