# lemniscat.plugin.awscli
A plugin to operate AWS services through AWS cli into a lemniscat workflow

## Description
This plugin allows you to operate AWS services through AWS cli into a lemniscat manifest.

## Usage
### Pre-requisites
In order to use this plugin, you need to have an AWS account and an AWS user. You can create a user using the AWS CLI, PowerShell, or the AWS console. The service principal is used to authenticate the AWS CLI to your AWS account.

After that you to be sure that you have the AWS CLI installed on your agent. You can install it using the following command:

#### Linux
```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

#### Windows
```powershell
msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi
```

You need also set environment variables to authenticate the AWS CLI to your AWS account.
- `AWS_ACCESS_KEY_ID` : The access key ID of the AWS user
- `AWS_SECRET_ACCESS_KEY` : The secret access key of the AWS user
- `AWS_DEFAULT_REGION` : The default region to use, for example `us-west-2`

You need to add plugin into the required section of your manifest file.
```yaml
requirements:
  - name: lemniscat.plugin.awscli
    version: 0.1.0.9
```

### Running powershell commands with AWS CLI
```yaml
- task: awscli
  displayName: 'AWS CLI'
  steps:
    - run
  parameters:
    scripttype: pwsh
    commandtype: inline
    script: |
      $version = az --version
      Write-Host "AWS CLI version: $version"
```

### Running powershell script with AWS CLI
```yaml
- task: awscli
  displayName: 'AWS CLI'
  steps:
    - run
  parameters:
    scripttype: pwsh
    commandtype: file
    filePath: ${{ workingdirectory }}/scripts/ClearAWSBucket.ps1
    fileParams:
      bucketname: ${{ bucketName }}
```
### Running powershell commmands and pass variables through json file
> [!NOTE] 
> This feature is particulary recommand when you need to manipulate complexe variable with your task.
> You can access to the variables in the json file by using the following command:
> ```powershell
> $location = Get-Location
> $variables = Get-Content "$($location.path)/vars.json" | ConvertFrom-Json -Depth 100
> ```

```yaml
- task: awscli
  displayName: 'AWS CLI'
  steps:
    - run
  parameters:
    scripttype: pwsh
    commandtype: inline
    script: |
      $location = Get-Location
      $variables = Get-Content "$($location.path)/vars.json" | ConvertFrom-Json -Depth 100
      $version = az --version
      Write-Host "AWS CLI version: $version"
    storeVariablesInFile:
      format: json
      withSecrets: false
```

## Inputs

### Parameters
- `scripttype`: The type of the script to run. It can be only `pwsh` (for the moment)
- `commandtype`: The type of the command to run. It can be `inline` or `file`
- `script`: The script to run. It can be a powershell command line. It is used only if `commandtype` is `inline`
- `filePath`: The path of the powershell script file (*.ps1) to run. It is used only if `commandtype` is `file`
- `fileParams`: The parameters to pass to the powershell script file. It is used only if `commandtype` is `file`
- [`storeVariablesInFile`](#StoreVariablesInFile): Describe the way to store the variables in a file to used in the task.

#### StoreVariablesInFile
- `format`: The format of the file to store the variables. It can be `json` or `yaml`
- `withSecrets`: A boolean value to indicate if the secrets should be stored in the file. It can be `true` or `false`

## Outputs

You can push variables to the lemniscat runtime in order to be used after by other tasks.
To do that, you need to use `Write-Host` command in your powershell script to push variables to the lemniscat runtime.
You must use the following format to push variables to the lemniscat runtime:
`[lemniscat.pushvar] <variableName>=<variableValue>`

For example:

```powershell
Write-Host "[lemniscat.pushvar] workspaceExist=$workspaceExist"
```

You can specify the sensitivity of the variable by adding `secret` like this :
`[lemniscat.pushvar.secret] <variableName>=<variableValue>`

For example:

```powershell
Write-Host "[lemniscat.pushvar.secret] storageAccountKey=$storageAccountKey"
```

By default all variable are considered as string. If you want to specify the type of the variable, you can add the type after the variable name like this:
`[lemniscat.pushvar(<variableType>)] <variableName>=<variableValue>`

`variableType` can be `string`, `int`, `bool`, `float`, `json` (for complexe object)

For example:

```powershell
Write-Host "[lemniscat.pushvar(int)] numberOfFiles=$numberOfFiles"
```