pipeline {
    agent { label "TL" }

    stages {
        stage('Generate Report') {
            steps {
                script{
                    cleanWs()
                    checkout scm

                    docker.image('python:3.8').inside("-v ${WORKSPACE}:/app -u root ") {
                        sh """
                            cp -r /app/tcms.conf /etc/
                            pip install -r requirements.txt
                            rm -f /etc/localtime && ln -s /usr/share/zoneinfo/Asia/Singapore /etc/localtime
                            python main.py -epic_ticket $epic_ticket -test_run_ids $test_run_ids -testing_conclusion $testing_conclusion -project_name $project_name
                            project_name=$project_name epic_ticket=$epic_ticket  python submit_report.py
                        """
                    }

                    email_list = "xx@example.com"
                    report_date = new Date().format("yyyyMMddHH")

                    docker.image('cypress/included:12.6.0').inside("-v ${WORKSPACE}:/app -u root --entrypoint='' ") {
                        sh """
                            cd /app
                            npm i markdown-to-html-cli -g
                            markdown-to-html --style=github-style.css --source ${project_name}/${epic_ticket}_TestingReport_${report_date}.md --output TestingReport.html
                        """
                    }
                }
            }
            post {
                success {
                    emailext (
                        subject: "[${epic_ticket}] ${project_name} Testing Report ${report_date}",
                        body:  '''${FILE, path="TestingReport.html"}''',
                        mimeType: 'text/html',
                        to: "$email_list",
                        recipientProviders: [[$class: 'CulpritsRecipientProvider']]
                    )
                }
            }
        }
    }
}