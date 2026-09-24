targetScope = 'resourceGroup'

@description('Globally unique Azure Storage account name')
@minLength(3)
@maxLength(24)
param storageAccountName string

@description('Azure region used for the storage account')
param location string = resourceGroup().location

resource evidenceStorage 'Microsoft.Storage/storageAccounts@2025-08-01' = {
  name: storageAccountName
  location: location

  sku: {
    name: 'Standard_LRS'
  }

  kind: 'StorageV2'

  properties: {
    accessTier: 'Hot'


    minimumTlsVersion: 'TLS1_2'


    supportsHttpsTrafficOnly: true


    allowBlobPublicAccess: false


    allowSharedKeyAccess: false


    defaultToOAuthAuthentication: true

    // Keep the public endpoint enabled so approved network rules can
    // be added later. The network ACL must deny traffic by default.
    publicNetworkAccess: 'Enabled'

    networkAcls: {

      bypass: 'None'


      defaultAction: 'Deny'

      ipRules: []
      virtualNetworkRules: []
    }
  }
}

output storageAccountId string = evidenceStorage.id
output storageAccountName string = evidenceStorage.name
