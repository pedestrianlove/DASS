{{/*
Expand the name of the chart.
*/}}
{{- define "meta-chart.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "meta-chart.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "meta-chart.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "meta-chart.labels" -}}
helm.sh/chart: {{ include "meta-chart.chart" . }}
{{ include "meta-chart.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "meta-chart.selectorLabels" -}}
app.kubernetes.io/name: {{ include "meta-chart.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "meta-chart.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "meta-chart.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{- define "meta-chart.backendConfigName" -}}
{{- printf "%s-backend-config" .Release.Name -}}
{{- end }}

{{- define "meta-chart.backendSecretName" -}}
{{- printf "%s-backend-secret" .Release.Name -}}
{{- end }}

{{- define "meta-chart.frontendConfigName" -}}
{{- printf "%s-frontend-config" .Release.Name -}}
{{- end }}

{{- define "meta-chart.postgresHost" -}}
{{- default "postgres" .Values.postgres.primaryServiceName -}}
{{- end }}

{{- define "meta-chart.postgresReplicaHost" -}}
{{- default "postgres-replica" .Values.postgres.replicaServiceName -}}
{{- end }}

{{- define "meta-chart.localstackHost" -}}
{{- default "localstack" .Values.localstack.fullnameOverride -}}
{{- end }}

{{- define "meta-chart.localstackFqdn" -}}
{{- printf "%s.%s.svc.cluster.local" (include "meta-chart.localstackHost" .) .Release.Namespace -}}
{{- end }}

{{- define "meta-chart.apiHost" -}}
{{- default "api-server" (index .Values "api-server").fullnameOverride -}}
{{- end }}

{{- define "meta-chart.postgresExporterName" -}}
{{- printf "%s-postgres-exporter" .Release.Name -}}
{{- end }}

{{- define "meta-chart.sqsExporterName" -}}
{{- printf "%s-sqs-exporter" .Release.Name -}}
{{- end }}
