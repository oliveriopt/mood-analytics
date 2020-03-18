#!/usr/bin/env groovy

import groovy.json.JsonSlurperClassic

def started = System.currentTimeMillis()

def getDuration() {
    return System.currentTimeMillis() - started
}

def runStep(name, fn) {
  stage(name) {
    try {
      fn()
    } catch (exception) {
      reportPRstatus("failure", "Pipeline failure on step: $name")

      //Trigger slack notification
      notify(color: 'danger',message: "Error in *`${name}`* step.\n- *Branch:* ${BRANCH_NAME}\n- *Repository:* mood-analytics\n- *Build:* <${BUILD_URL}|#${BUILD_NUMBER}>\n- *Author:* ${gitCommitAuthor()}\n- *Commit message:* ${gitCommitMessage()}")

      throw exception
    }
  }
}

def reportPRstatus(state, message) {
  def body = "{\"state\": \"$state\",\"description\": \"$message\",\"context\":\"pipeline\",\"target_url\":\"${BUILD_URL}\"}"
  def url = "${env.GITHUB_API_URL}/repos/kununu/mood-analytics/statuses/${gitHash('')}?access_token=${env.GITHUB_API_TOKEN}"
  sh("curl -sS -o nul -X POST '$url' -d '$body'")
}

def scm_checkout() {
    checkout scm

    dir('DevopsRepo') {
        checkout([
            $class: 'GitSCM',
            branches: [[name: 'origin/master']],
            userRemoteConfigs: [[url: 'git@github.com:kununu/mood-devops.git']]
        ])
    }
}

node {
    ansiColor('xterm') {
        def branch = env.BRANCH_NAME
        def environment = "staging"
        if(env.BRANCH_NAME.startsWith("feature")) {
            branch = "${env.BRANCH_NAME}".split('/')[1]
        }

        scm_checkout()

        def imageTag = "${branch}-${gitHash()}"
        def deploymentName = "${branch}-analytics"
        def image = "eu.gcr.io/mood-171312/mood-analytics:${imageTag}"
        def sonarqubeJob = "/testing/sonar-publish/validation-sonar-publish"
        def jenkinsHome = env.JENKINS_HOME
        def jenkinsURL = env.JENKINS_URL
        def domain = "engage.kununu.it"
        def fqdn = "${branch}-api.${domain}"
        def url = "https://${branch}.${domain}"
        def insightsDBName = "mood_insights_${branch}"
        def insightsAPIName = "mood_${branch}"
        def helmPath = "./DevopsRepo/analytics"

        runStep('Check cluster availability') {
            sh("./DevopsRepo/scripts/wait-for-connection.sh ${jenkinsURL} deployment")
        }

        runStep('Build image') {
            sh("docker build -t 'mood-analytics:build' -f deployment/Dockerfile .")
        }

        runStep('Run tests') {
            // Create JENKINS reports folder
            sh("mkdir -p /opt/mood/tmp/reports/analytics/${BRANCH_NAME}")

            // Run tests
            sh("docker run \
                -e APP_ENV=deploy \
                -e GOOGLE_NLP_CREDENTIALS=/app/keys/mood-2364f0d6fc3e.json \
                -v /opt/mood/tmp/reports/analytics/${BRANCH_NAME}:/tests_coverage mood-analytics:build /app/run_tests.sh")
        }

        runStep('Create database') {
            dir('DevopsRepo/scripts') {
              def statusCode =  sh(script:""". /opt/mood/set_database_envs.sh 2>/dev/null &&
                                           ./dbrelease.sh staging staging mood_develop ${insightsAPIName} &&
                                           ./dbrelease.sh staging staging mood_insights_develop ${insightsDBName}""", returnStatus:true)
              if(statusCode != 0 ) {
                  error("Error: helm install failed copying the database. Please check logs.")
              }
            }
        }

        runStep('Push image to registry') {
            sh("docker build -t '${image}' -f deployment/Dockerfile.final .")
            sh("docker push ${image}")
        }

        runStep('Deployment') {
            
            def status = sh(script: "helm status ${deploymentName}", returnStatus: true)

            if(status != 0) {
                def statusCode = sh(script:"helm install --set image.tag=${imageTag} --set image.branch=${branch} --set env.insightsDatabase=${insightsDBName} --set env.appENV=${branch} --set env.apiDatabase=${insightsAPIName} --namespace=${environment} --name=${deploymentName} -f ${helmPath}/charts/${environment}/values.yaml ${helmPath}", returnStatus:true)

                // If install fails for some reason (e.g. configuration issues on yaml) -> purge pushed image
                // This avoids manual intervention
                if(statusCode != 0 ) {
                    sh("helm delete --purge ${deploymentName}")
                    error("Error: helm install failed for some reason. Please check logs.")
                }
            } else {
                sh("helm upgrade --set image.tag=${imageTag} --set image.branch=${branch} --set env.insightsDatabase=${insightsDBName} --set env.appENV=${branch} --set env.apiDatabase=${insightsAPIName} -f ${helmPath}/charts/${environment}/values.yaml ${deploymentName} ${helmPath}")
            }

            //Trigger slack notification
            notify(color: 'good',message: "Successful deploy!\n- *Branch:* ${BRANCH_NAME}\n- *Repository:* mood-analytics\n- *Build:* <${BUILD_URL}|#${BUILD_NUMBER}>\n- *Author:* ${gitCommitAuthor()}\n- *Commit message:* ${gitCommitMessage()}")
        }

        runStep('Sonar Publish') {
            build job: "${sonarqubeJob}", parameters: [
                string(name:'BRANCH', value: "${BRANCH_NAME}"),
                string(name:'ENGAGE_PROJECT', value: "${MOOD_ANALYTICS}")
            ]
        }

        runStep('Report PR status') {
          reportPRstatus("success", "Pipeline is ok!")
        }
    }
}

def gitHash(opt='--short') {
  sh "git rev-parse $opt HEAD > .git/commit-id"
  return readFile('.git/commit-id').trim()
}

def notify(Map args) {
  String channel = args.channel ? args.channel : '#mood-deploy'
  slackSend channel: channel, color: args.color, message: args.message
}

def gitCommitMessage() {
  return sh(
    script: "git log -1 --pretty=format:'%s [%h]'",
    returnStdout: true
  ).trim()
}

def gitCommitAuthor() {
  return sh(
    script: "git log -1 --pretty=format:'%an'",
    returnStdout: true
  ).trim()
}
