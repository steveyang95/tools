import pprint
import json
import boto3
from botocore.exceptions import ClientError
import jmespath
import pprint
import time

# Globals
pp = pprint.PrettyPrinter(indent=4)


############
# SimpleDB #
############


class SimpleDbHelper(object):
    def __init__(self, profile="default", region="us-west-2"):
        """INPUTS:
                profile (str)     : AWS profile to use for session
                                    Default: default
                                    OPTIONAL
            OUTPUTS:
                None
        """
        boto3.setup_default_session(profile_name=profile)
        self.sdb_client = boto3.client('sdb', region_name=region)

    def get_domain_metadata(self, domain_name):
        """Retrieves the domain's metadata.
        Response Syntax:
            {
                'ItemCount': 123,
                'ItemNamesSizeBytes': 123,
                'AttributeNameCount': 123,
                'AttributeNamesSizeBytes': 123,
                'AttributeValueCount': 123,
                'AttributeValuesSizeBytes': 123,
                'Timestamp': 123
            }

            INPUT:
                domain_name (str) : SimpleDB domain name
                                    REQUIRED
        """
        self._validate_input({'domain_name': domain_name}, "GetDomainMetadata")
        print('SimpleDBHelper::GetDomainMetadata: Domain {}'.format(domain_name))
        resp = None
        try:
            resp = self.sdb_client.domain_metadata(
                DomainName=domain_name
            )
        except ClientError as e:
            if e.response['Error']['Code'] == "NoSuchDomain":
                return None
        return resp

    def create_domain(self, domain_name):
        """Creates SimpleDB domain.
        It takes at least 10 seconds (maybe more) for AWS to create a domain.

            INPUT:
                domain_name (str) : SimpleDB domain name
                                    REQUIRED
        """
        self._validate_input({'domain_name': domain_name}, "CreateDomain")
        print('SimpleDBHelper::CreateDomain: {}'.format(domain_name))
        self.sdb_client.create_domain(
            DomainName=domain_name
        )
        time.sleep(15)

    def put_attributes(self, domain_name, item_name, attrs):
        """Put attributes into SimpleDB domain.
            INPUT:
                domain_name (str) : SimpleDB domain name
                                    REQUIRED
                item_name (str)   : Name of item.  Similar to rows on a spreadsheet. Items represent individual
                                    objects that contain one or more value-attribute pairs
                                    REQUIRED
                attrs (list)      : List of Attributes. An attribute is of format:
                                    {
                                        'Name': 'string',
                                        'Value': 'string',
                                        'Replace': True|False
                                    }
                                    REQUIRED
        """
        self._validate_input({'domain_name': domain_name,
                              'item_name': item_name,
                              'attrs': attrs}, "PutAttributes")
        print('SimpleDB::PutAttributes: Attrs {}'.format(attrs))
        self.sdb_client.put_attributes(
            DomainName=domain_name,
            ItemName=item_name,
            Attributes=attrs
        )

    def delete_attributes(self, domain_name, item_name, attrs):
        """Delete attributes from SimpleDB domain.
            INPUT:
                domain_name (str) : SimpleDB domain name
                                    REQUIRED
                item_name (str)   : Name of item.  Similar to rows on a spreadsheet. Items represent individual
                                    objects that contain one or more value-attribute pairs
                                    REQUIRED
                attrs (list)      : List of Attributes. An attribute is of format:
                                    {
                                        'Name': 'string',
                                        'Value': 'string',
                                        'Replace': True|False
                                    }
                                    REQUIRED
        """
        self._validate_input({'domain_name': domain_name,
                              'item_name': item_name,
                              'attrs': attrs}, "PutAttributes")
        print('SimpleDB::DeleteAttributes: Attrs {}'.format(attrs))
        self.sdb_client.delete_attributes(
            DomainName=domain_name,
            ItemName=item_name,
            Attributes=attrs
        )

    def batch_delete_attributes(self, domain_name, items):
        """Batch delete attributes from SimpleDB domain.
        Limits:
            - 1 MB request size
            - 25 item limit per BatchDeleteAttributes operation

            INPUT:
                domain_name (str) : SimpleDB domain name
                                    REQUIRED
                items (list)      : List of Items with Attributes. Format:
                                    [{
                                        'Name': 'string',
                                        'Attributes': [{ 'Name' : 'string', 'Value' : 'string' },]
                                    },]
                                    REQUIRED
        """
        print('SimpleDB::BatchDeleteAttributes: Items {}'.format(items))
        self.sdb_client.batch_delete_attributes(
            DomainName=domain_name,
            Items=items
        )

    def get_attributes(self, domain_name, item_name, attr_names):
        """Get attributes associated with specified item from SimpleDB domain.
            INPUT:
                domain_name (str) : SimpleDB domain name
                                    REQUIRED
                item_name (str)   : Name of item.  Similar to rows on a spreadsheet. Items represent individual
                                    objects that contain one or more value-attribute pairs
                                    REQUIRED
                attr_names (list) : List of Attribute Names
                                    REQUIRED
        """
        self._validate_input({'domain_name': domain_name,
                              'item_name': item_name,
                              'attr_names': attr_names}, "PutAttributes")
        print('SimpleDB::DeleteAttributes: Attribute Names {}'.format(attr_names))
        resp = self.sdb_client.get_attributes(
            DomainName=domain_name,
            ItemName=item_name,
            AttributeNames=attr_names,
            ConsistentRead=True
        )
        print('AWSQA::SimpleDB: Response: {}'.format(resp))
        return resp['Attributes']

    def delete_domain(self, domain_name):
        """Deletes SimpleDB domain.
        It takes at least 10 seconds (maybe more) for AWS to delete a domain.

            INPUT:
                domain_name (str) : SimpleDB domain name
                                    REQUIRED
        """
        self._validate_input({'domain_name': domain_name}, "DeleteDomain")
        print('SimpleDB::DeleteDomain: {}'.format(domain_name))
        self.sdb_client.delete_domain(
            DomainName=domain_name
        )
        time.sleep(15)

    def list_domains(self):
        """Lists all domains in SimpleDB.

        """
        resp = self.sdb_client.list_domains()
        domain_names = resp['DomainNames'] if 'DomainNames' in resp else []
        while 'NextToken' in resp:
            resp = self.sdb_client.list_domains(NextToken=resp['NextToken'])
            domain_names += resp['DomainNames']

        return domain_names

    def select(self, query):
        """Query SimpleDB Table

        :param query: (str) SQL query string
        :return: (dict) { 'Items': [ <SimpleDB_Attribute>, ...], 'NextToken': 'string' }
        """
        resp = self.sdb_client.select(
            SelectExpression=query,
            ConsistentRead=True
        )
        return resp

    def display_items(self, domains):
        """Displays all the items in each of the domains requested.
            INPUT:
                domains (list) : List of domain names
        """
        for d in domains:
            query = 'select * from `{}`'.format(d)
            resp = self.select(query)
            print('\nHere is the response for domain {}'.format(d))
            if 'Items' in resp:
                items = resp['Items']
                for i, item in enumerate(items):
                    print("=" * 20 + str(i) + "=" * 20)
                    pp.pprint(item)
                    print("=" * 41)
            else:
                print("Empty response")
                pprint.pprint(resp, indent=4)

    ###################
    # Private Methods #
    ###################

    def _validate_input(self, params, method):
        """Validates all the input params and makes sure that they are present.
        If not, then raise an Exception.

            INPUT:
                params (dict) : Keys are the param names and values are the input
                                REQUIRED
                method (str)  : Name of the method where input validation is happening
                                REQUIRED
        """
        for key, val in params.iteritems():
            if not val:
                raise Exception("SimpleDB::{}Error: {} cannot be None.".format(method, key))

def cleanup_simpledb_domains(sdb):
    """There is a limit on how many simpledb domains that each region has. Our controller
    does not clean up after itself and we have no way of cleaning up atm. Have this for the
    tests so far until cleanup has been implemented.

    :return:
    """
    # Prefixes are from plt/controller/db.py
    simpledb_domains_prefixes = ["subscriptions", "config", "sessions"]

    domains = sdb.list_domains()

    for domain in domains:
        if domain.startswith("subscriptionsX") or domain.startswith("configX") or domain.startswith("sessionsX"):
            print('\nDeleting domain "{}"...'.format(domain))
            try:
                sdb.delete_domain(domain)
                print('\nSuccessfully deleted domain "{}"'.format(domain))
            except Exception as e:
                print("\nUnable to delete domain {}. Error: {}".format(domain, e))


###############
# Main Helper #
###############


def interact():
    list_of_actions = ['create_domain', 'check_domain', 'list_domain', 'delete_domain', 'select', 'display_items',
                       'delete_attrs', 'delete_controller_domains']

    action_index = raw_input("\nInput index of which action you would like to take\n"
                             "(0) create domain | (1) domain exists | (2) list domains | "
                             "(3) delete domain | (4) query domain | (5) display items | "
                             "(6) delete attrs | (7) delete controller domains"
                             "\nAction Index: ")
    action_index = int(action_index)

    actions_keymap = {}
    for action in list_of_actions:
        if action == list_of_actions[action_index]:
            actions_keymap[action] = True
        else:
            actions_keymap[action] = False

    params = {}
    if action_index in [0, 1, 3, 5, 6]:
        params['domain'] = raw_input("\nPlease input domain name: ")
    elif action_index in [4]:
        params['query'] = raw_input("\nPlease input query: ")

    if action_index in [6]:
        params['item_name'] = raw_input("\nPlease input item name: ")
        try:
            params['attrs'] = [json.loads(raw_input("\nPlease enter one attribute to delete. Please use double quotes. "
                                                    "Must be of form {'Name' : 'string', 'Value': 'string'}: "))]
        except ValueError as e:
            print("Please use double quotes instead of single quotes.\n\tError: {}".format(e))
            params['attrs'] = [json.loads(raw_input("\nPlease enter one attribute to delete. "
                                                    "Must be of form {'Name' : 'string', 'Value': 'string'}: "))]

    return actions_keymap, params


if __name__ == "__main__":
    profile = raw_input("AWS Profile [Enter is 'default']: ")
    if not profile:
        profile = 'default'
    region = raw_input("Region [Enter is 'us-west-2']: ")
    sdb = SimpleDbHelper(profile)
    if region:
        sdb = SimpleDbHelper(profile, region)

    while True:
        actions_keymap, params = interact()
        domain = params['domain'] if 'domain' in params else None
        query = params['query'] if 'query' in params else None
        item_name = params['item_name'] if 'item_name' in params else None
        attrs = params['attrs'] if 'attrs' in params else None

        if actions_keymap['check_domain']:
            if not domain:
                msg = 'Following parameters required:' \
                      '\n\tDomain: {}'.format(domain)
                print(msg)
                continue
            print('\nChecking if domain \'{}\' exists...'.format(domain))
            resp = sdb.get_domain_metadata(domain)
            if resp:
                print("Domain {} exists\n".format(domain))
            else:
                print("Domain {} does not exist.\n".format(domain))

        if actions_keymap['list_domain']:
            print("\nListing all domains in SimpleDB...")
            domains = sdb.list_domains()
            pprint.pprint(domains, indent=4)

        if actions_keymap['create_domain']:
            if not domain:
                msg = 'Following parameters required:' \
                      '\n\tDomain: {}'.format(domain)
                print(msg)
                continue
            print("\nCreating domain '{}'...".format(domain))
            sdb.create_domain(domain)
            print('\nSuccessfully created domain "{}"'.format(domain))

        if actions_keymap['delete_domain']:
            if not domain:
                msg = 'Following parameters required:' \
                      '\n\tDomain: {}'.format(domain)
                print(msg)
                continue
            print('\nDeleting domain "{}"...'.format(domain))
            sdb.delete_domain(domain)
            print('\nSuccessfully deleted domain "{}"'.format(domain))

        if actions_keymap['select']:
            if not query:
                msg = 'Following parameters required:' \
                      '\n\tQuery: {}'.format(query)
                print(msg)
                continue
            print('\nQuerying using string "{}"...'.format(query))
            try:
                resp = sdb.select(query)
                pprint.pprint(resp, indent=4)
            except Exception as e:
                print("\nSDBCLI::Select Query raised exception: {}".format(e))

        if actions_keymap['display_items']:
            if not domain:
                msg = 'Following parameters required:' \
                      '\n\tDomain: {}'.format(domain)
                print(msg)
                continue
            print('\nListing entries in domain "{}"'.format(domain))
            try:
                sdb.display_items([domain])
            except Exception as e:
                print("\nSDBCLI::Display Items raised exception: {}".format(e))

        if actions_keymap['delete_attrs']:
            if not (domain and item_name and attrs):
                msg = 'Following parameters required:' \
                      '\n\tDomain: {}' \
                      '\n\tItem Name: {}' \
                      '\n\tAttrs: {}'.format(domain, item_name, attrs)
                print(msg)
                continue
            print('\nDeleting attribute {} from domain "{}"'.format(attrs, domain))
            try:
                sdb.delete_attributes(domain, item_name, attrs)
            except Exception as e:
                print("\nSDBCLI::Delete Attributes raised exception: {}".format(e))

        if actions_keymap['delete_controller_domains']:
            cleanup_simpledb_domains(sdb)

        answer = raw_input("\nWould you like to take another action? (y/N) ")
        if answer.lower() not in ['y', 'yes', 'ye']:
            break
