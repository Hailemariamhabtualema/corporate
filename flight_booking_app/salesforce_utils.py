import sys
print("Python Path:", sys.path)
print("Python Version:", sys.version)

from simple_salesforce import Salesforce
from django.conf import settings
from flight_booking.salesforce_config import (
    SF_CLIENT_ID,
    SF_CLIENT_SECRET,
    SF_USERNAME,
    SF_PASSWORD,
    SF_SECURITY_TOKEN,
    SF_INSTANCE_URL,
    SF_API_VERSION
)

class SalesforceConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SalesforceConnection, cls).__new__(cls)
            cls._instance.sf = None
        return cls._instance

    def connect(self):
        """Establish connection to Salesforce"""
        if self.sf is None:
            try:
                self.sf = Salesforce(
                    username=SF_USERNAME,
                    password=SF_PASSWORD,
                    security_token=SF_SECURITY_TOKEN,
                    instance_url=SF_INSTANCE_URL,
                    version=SF_API_VERSION
                )
            except Exception as e:
                print(f"Error connecting to Salesforce: {str(e)}")
                raise
        return self.sf

    def create_record(self, object_name, data):
        """Create a new record of any type in Salesforce"""
        sf = self.connect()
        try:
            print(f"Creating new {object_name} record with data: {data}")
            result = getattr(sf, object_name).create(data)
            print(f"Create result: {result}")
            return result
        except Exception as e:
            print(f"Error creating {object_name} record: {str(e)}")
            raise

    def create_lead(self, lead_data):
        """Create a new lead in Salesforce"""
        return self.create_record('Lead', lead_data)

    def create_opportunity(self, opp_data):
        """Create a new opportunity in Salesforce"""
        return self.create_record('Opportunity', opp_data)

    def create_contact(self, contact_data):
        """Create a new contact in Salesforce"""
        return self.create_record('Contact', contact_data)

    def create_corporate_account(self, account_data):
        """Create a new Corporate Account in Salesforce"""
        return self.create_record('Corporate_Account__c', account_data)

    def update_account(self, account_id, account_data):
        """Update a Corporate Account in Salesforce"""
        sf = self.connect()
        try:
            print(f"Attempting to update Corporate_Account__c with ID: {account_id}")
            print(f"Update data: {account_data}")
            result = sf.Corporate_Account__c.update(account_id, account_data)
            print(f"Update result: {result}")
            return result
        except Exception as e:
            print(f"Error updating Corporate Account: {str(e)}")
            raise

    def query(self, soql_query):
        """Execute a SOQL query"""
        sf = self.connect()
        try:
            print(f"Executing SOQL query: {soql_query}")
            result = sf.query(soql_query)
            print(f"Query result: {result}")
            return result
        except Exception as e:
            print(f"Error executing query: {str(e)}")
            raise

    def Account(self):
        """Get Account object for updates"""
        sf = self.connect()
        return sf.Account

    def get_or_create_corporate_account(self, username):
        """Get or create a Corporate Account for the given username"""
        sf = self.connect()
        try:
            # Try to find existing account
            query = f"SELECT Id, Total_Points__c FROM Corporate_Account__c WHERE Name = '{username}'"
            result = self.query(query)
            
            if result['totalSize'] > 0:
                return result['records'][0]
            else:
                # Create new account
                account_data = {
                    'Name': username,
                    'Total_Points__c': 0
                }
                create_result = self.create_corporate_account(account_data)
                return {'Id': create_result['id'], 'Total_Points__c': 0}
        except Exception as e:
            print(f"Error in get_or_create_corporate_account: {str(e)}")
            raise

# Create a singleton instance
salesforce = SalesforceConnection() 