#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = ["Pablo ALINGERY, Nima TRAORE"]

from sys import stdout, stderr
from datetime import datetime, timedelta
from future.moves.urllib.parse import urlencode
from future.moves.urllib.request import urlopen, urlretrieve
from future.moves.urllib.error import HTTPError
from simplejson import load
from xml.dom.minidom import parseString

from sitools2.core.field import Field


class Dataset:
    """Class defining a Sitools2 dataset.

    Attributes defined here:
        allowed_filter_list: list of attributes of filtered field objects
        allowed_sort_list: list of attributes of sorted field objects
        description: description of the dataset
        download_type: type of the download to be used (TAR, ZIP or Tar.gz)
        fields_dict: dictionary of fields (key = name of the field)
        fields_list: list of field objects (instances of the class Field)
        filter_list: list of field objects that can be filtered
        name: name of the dataset
        no_client_access_list: list of restricted fields for the web user
        primary_key: field object of the primary in sitools2 database
        resources_target: list of resources (tar, zip, plugin etc.) associated with the dataset
        sort_list: list of field objects that can be sorted
        uri: URI of the dataset
        url: URL of the datatset

    Methods defined here:
        build_output_objects(): build output objects (list and dict)
        build_sort_options(): build sort output options
        compute_attributes(): compute attributes from web service answer
        create_url_options(): create url options
        execute_plugin(): downloads a selection of data
        get_pk_item_component(): return split of primary key component
        get_result_count(): get result count from url_count
        get_result_dict(): get result in dictionary type
        optimize_operation(): optimize operation value
        resources_list(): explores and lists dataset resources
        scan_limit_to_nb_res_max(): return nbr_results, kwargs, url
        search(): returns a list of dictionaries

    """
    def __init__(self, url):
        """Initializes class Dataset"""
        try:
            load(urlopen(url))
        except HTTPError:
            stderr.write(f"Error in Dataset.__init__() :\nDataset {url} is not available\nPlease send an email to "
                         "medoc-contact@ias.u-psud.fr to report an issue if the problem persists\n")
            raise
        self.name = ""
        self.description = ""
        self.uri = "/" + url.split("/")[-1]
        self.url = url
        self.fields_list = []
        self.fields_dict = {}
        self.filter_list = []
        self.allowed_filter_list = []
        self.sort_list = []
        self.allowed_sort_list = []
        self.resources_target = []
        self.no_client_access_list = []
        self.primary_key = None
        self.compute_attributes()
        self.resources_list()
        self.download_type = ""
    
    def compute_attributes(self, **kwargs):
        """Compute attributes of dataset from web service answer"""
        kwargs.update({'media': 'json'})
        url = self.url + '?' + urlencode(kwargs)
        try:
            result = load(urlopen(url))
            self.name = result['dataset']['name']
            self.description = result['dataset']['description']
            columns = result['dataset']['columnModel']
            for column in columns:
                self.fields_list.append(Field(column))
                self.fields_dict.update({column['columnAlias']: Field(column)})
                if column['filter']:
                    self.filter_list.append(Field(column))
                if 'sortable' in column and column['sortable']:
                    self.sort_list.append(Field(column))
                if 'primaryKey' in column and column['primaryKey']:
                    self.primary_key = (Field(column))
                if 'columnRenderer' in column and column['columnRenderer']['behavior'] == "noClientAccess":
                    self.no_client_access_list.append(column['columnAlias'])
        except HTTPError:
            stderr.write("Error in Dataset.compute_attributes(), please report it to medoc-contact@ias.u-psud.fr\n")
            raise
        for field in self.filter_list:
            self.allowed_filter_list.append(field.name)
        for field in self.sort_list:
            self.allowed_sort_list.append(field.name)

    def resources_list(self):
        """Explores and lists dataset resources"""
        try:
            wadl_url = self.url + "?method=OPTIONS"
            url = urlopen(wadl_url)
            wadl = url.read()
            domwadl = parseString(wadl)
            resources = domwadl.getElementsByTagName('resource')
            for i in range(len(resources)):
                self.resources_target.append(self.url + "/" + resources[i].getAttribute('path'))
        except HTTPError:
            stderr.write("Error in Dataset.ressources_list() not accessible, please report it to "
                         "medoc-contact@ias.u-psud.fr\n")
            raise

    def display(self):
        """Output attributes of Dataset"""
        print(self.__repr__())

    def __repr__(self):
        """Representation of an instance of Dataset.

        Returns:
        All info available for a dataset

        """
        n_tab_str = "\n\t\t\t%d) %s"
        phrase = ""
        phrase += ("\n\nDataset object display() :\n\t%s\n\t\tdescription : %s\n\t\turi : %s\n\t\turl : %s\n\t\t"
                   "primary_key : %s" % (self.name, self.description, self.uri, self.url, self.primary_key.name))
        phrase += "\n\t\tresources_list :"
        for i, res in enumerate(self.resources_target):
            phrase += n_tab_str % (i, res)
        phrase += "\n\t\tfields list :"
        for i, field in enumerate(self.fields_list):
            phrase += n_tab_str % (i, str(field.name))
        phrase += "\n\t\tfilter list :"
        for i, field in enumerate(self.filter_list):
            phrase += n_tab_str % (i, str(field.name))
        phrase += "\n\t\tsort list :"
        for i, field in enumerate(self.sort_list):
            phrase += n_tab_str % (i, str(field.name))
        return phrase

    @staticmethod
    def optimize_operation(operation):
        """Optimizes operation.

        Returns:
            operation

        """
        if operation == 'GE':
            operation = 'GTE'
        elif operation == 'LE':
            operation = 'LTE'
        return operation

    def create_url_options(self, query_list, kwargs):
        """Creates url options.

        Args:
            query_list: list of query objects
            kwargs: url options

        Returns:
            kwargs

        """
        filter_counter = 0
        p_counter = 0
        str_filter = 'filter['
        for num_query, query in enumerate(query_list):
            # transform entries as upper letter
            operation = query.operation.upper()
            operation = self.optimize_operation(operation)
            if operation in ['LT', 'EQ', 'GT', 'LTE', 'GTE']:
                for field in query.fields_list:
                    if field.name not in self.allowed_filter_list:
                        error_msg = ("Error in Dataset.search() :\nfilter on %s is not allowed\n" % field.name)
                        stdout.write(error_msg)
                        raise ValueError(error_msg)
                kwargs.update({str_filter + str(filter_counter) + '][columnAlias]': "|".join(query.name_list),
                               str_filter + str(filter_counter) + '][data][type]': 'numeric',
                               str_filter + str(filter_counter) + '][data][value]': "|".join(query.value_list),
                               str_filter + str(filter_counter) + '][data][comparison]': operation})
                filter_counter += 1
            elif operation in ['LIKE']:
                p_counter += 1
            elif operation in ['IN']:
                operation = 'LISTBOXMULTIPLE'
                kwargs.update({'p[' + str(p_counter) + ']': operation + "|" + "|".join(
                    query.name_list) + "|" + "|".join(query.value_list)})
                p_counter += 1
            elif operation in ['DATE_BETWEEN', 'NUMERIC_BETWEEN', 'CADENCE']:
                kwargs.update({'p[' + str(p_counter) + ']': operation + "|" + "|".join(
                    query.name_list) + "|" + "|".join(query.value_list)})
                p_counter += 1
            else:
                allowed_operations = "ge, le, gte, lte, lt, eq, gt, lte, like, in, numeric_between, date_between"
                error_msg = ("Operation not available : %s \nAllowed operations are : %s\n" %
                             (operation, allowed_operations))
                stderr.write(error_msg)
                raise ValueError(error_msg)

        return kwargs

    @staticmethod
    def build_output_objects(output_list):
        """Build output object list and output object dict

        Args:
            output_list: list of field objects

        Returns:
            (output_name_list, output_name_dict)

        """
        output_name_list = []
        output_name_dict = {}
        for i, field in enumerate(output_list):
            output_name_list.append(str(field.name))
            output_name_dict.update({str(field.name): field})

        return output_name_list, output_name_dict

    def build_sort_options(self, sort_list):
        """Build sort output options.

        Args:
            sort_list: list of sorted field objects

        Returns:
            sort_dic_list

        """
        sort_dic_list = []
        for field in sort_list:
            if field[0].name not in self.allowed_sort_list:
                error_msg = ("Error in Dataset.search():\nsort on %s is not allowed\n" % field.name)
                stderr.write(error_msg)
                raise ValueError(error_msg)
            sort_dictionary = {}
            sort_dictionary.update({"field": (str(field[0].name)), "direction": field[1]})
            sort_dic_list.append(sort_dictionary)

        return sort_dic_list

    def get_result_count(self, url_count):
        """Get result count from url_count.

        Args:
            url_count: url count

        Returns:
            result_count

        """
        try:
            result_count = load(urlopen(url_count))
        except HTTPError as e:
            stderr.write("HttpError exception\n")
            stderr.write("Error code : %s\n" % e.code)
            stderr.write("Error reason : %s\n" % e.reason)
            stderr.write("url : %s\n" % url_count)
            error_lines = e.readlines()
            out_msg = "Try later, contact medoc-contacts@ias.u-psud.fr if the problem persists\n"
            for line in error_lines:
                str_line = str(line)
                if "Datasource not activated" in str_line:
                    stderr.write("Explanation : Datasource %s not active\n" % self.name)
                    stderr.write(out_msg)
                    raise
                elif "Internal Server Error (500) - Error while querying datasource\n" in str_line:
                    stderr.write("Explanation : Error querying datasource %s\n" % self.name)
                    stderr.write(out_msg)
                    raise
            stderr.write(out_msg)
            raise
        else:
            return result_count

    def scan_limit_to_nb_res_max(self, nbr_results, url, temp_url, limit_to_nb_res_max, kwargs):
        """Scans limit_to_nb_res_max and return nbr_results, kwargs, url.

        Args:
            nbr_results: total number of results
            url: url
            temp_url: temporary url
            limit_to_nb_res_max: from the results sent by the server,
                limit to that value
            kwargs: url options

        Returns:
            (nbr_results, url, kwargs)

        """
        str_records = "/records"
        if 0 < limit_to_nb_res_max < kwargs['limit']:
            kwargs['limit'] = limit_to_nb_res_max
            kwargs['nocount'] = 'true'
            nbr_results = limit_to_nb_res_max
            url = self.url + str_records + '?' + urlencode(kwargs) + "&" + temp_url
        elif limit_to_nb_res_max > 0 and limit_to_nb_res_max >= kwargs['limit']:
            if limit_to_nb_res_max < nbr_results:
                nbr_results = limit_to_nb_res_max
            kwargs['nocount'] = 'true'
            url = self.url + str_records + '?' + urlencode(kwargs) + "&" + temp_url

        return nbr_results, url, kwargs

    def get_result_dict(self, data, output_name_list, output_name_dict):
        """Get result in dictionary.

        Args:
            data: temporary data loaded from the url
            output_name_list: output object list
            output_name_dict: output object dict

        Returns:
            {result_dict}

        """
        result_dict = {}
        for key, value in data.items():
            if (key not in self.no_client_access_list and key != 'uri' and key in output_name_list) or \
                    key in output_name_list:
                if output_name_dict[key].ftype.startswith('int'):
                    result_dict.update({key: int(value)})
                elif output_name_dict[key].ftype.startswith('float'):
                    result_dict.update({key: float(value)})
                elif output_name_dict[key].ftype.startswith('timestamp'):
                    (dt, m_secs) = value.split(".")
                    dt = datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")
                    m_seconds = timedelta(microseconds=int(m_secs))
                    result_dict.update({key: dt + m_seconds})
                else:
                    result_dict.update({key: value})

        return result_dict

    def search(self, query_list, output_list, sort_list, limit_request=350000, limit_to_nb_res_max=-1, **kwargs):
        """This is the generic search() method of a Sitools2 instance.

        Args:
            query_list: list of query objects
            output_list: list of field objects
            sort_list: list of sorted field objects
            limit_request: limit answers from server set by design to 350000
            limit_to_nb_res_max: from the results sent by the server, limit to that value

        Returns:
            List of dictionaries

        """
        str_records = "/records"
        kwargs.update({'media': 'json', 'limit': 300, 'start': 0})
        kwargs = self.create_url_options(query_list, kwargs)

        output_name_list, output_name_dict = self.build_output_objects(output_list)

        # build colModel url options
        kwargs.update({'colModel': '"' + ", ".join(output_name_list) + '"'})

        sort_dic_list = self.build_sort_options(sort_list)

        temp_kwargs = {}
        temp_kwargs.update({'sort': {"ordersList": sort_dic_list}})
        temp_url = urlencode(temp_kwargs).replace('+', '').replace('%27', '%22')

        # Build url just for count
        url_count = self.url + "/count" + '?' + urlencode(kwargs) + "&" + temp_url
        # Build url for the request
        url = self.url + str_records + '?' + urlencode(kwargs) + "&" + temp_url

        result_count = self.get_result_count(url_count)
        nbr_results = result_count['total']

        result = []
        # Check if the request does not exceed 350 000 items
        if nbr_results < limit_request:
            nbr_results, url, kwargs = self.scan_limit_to_nb_res_max(
                nbr_results, url, temp_url, limit_to_nb_res_max, kwargs)
            # Do the job per 300 items till nbr_result is reached
            # Check that request is done each 300 items
            while (nbr_results - kwargs['start']) > 0:
                result_temp = load(urlopen(url))
                for data in result_temp['data']:
                    result_dict = self.get_result_dict(data, output_name_list, output_name_dict)
                    result.append(result_dict)
                # Increment the job by the kwargs limit given (by design)
                kwargs['start'] += kwargs['limit']
                # Encode new kwargs and build new url for request
                url = self.url + str_records + '?' + urlencode(kwargs) + "&" + temp_url
                
            return result
        else:
            raise ValueError("Not allowed\nNbr results (%d) exceeds limit_request param: %d\n" %
                             (result_count['total'], limit_request))

    @staticmethod
    def get_pk_item_component(pk_item):
        """Return split of primary key item component.

        Args:
            pk_item: primary key item

        Returns:
            a list
        """
        if ',' in pk_item.component:
            pk_item_component = pk_item.component.split("||','||")
        elif '/' in pk_item.component:
            pk_item_component = pk_item.component.split("||'/'||")
        else:
            pk_item_component = pk_item.component.split()

        return pk_item_component

    def execute_plugin(self, plugin_name=None, pkey_values_list=None, filename=None, **kwargs):
        """Downloads a selection of data.

        Args:
            plugin_name: name of the plugin within sitools2
            pkey_values_list: list of primary key values for the current dataset
            filename: name of the downloaded file

        Returns:
            result execution of the plugin (can be TAR, ZIP or Tar.gz)

        """
        # Determine if primary key is a couple
        pk_item = self.fields_dict[self.primary_key.name]
        pk_item_component = self.get_pk_item_component(pk_item)

        # Primary key is like : (pk_item1, pk_item2)
        if len(pk_item_component) == 2:
            operation = 'LISTBOXMULTIPLE'
            pk_item1 = pk_item_component[0]
            pk_item2 = pk_item_component[1]
            recnum_list = [elmnt for idx, elmnt in enumerate(pkey_values_list) if idx % 2 == 0]
            series_name_list = [elmnt for idx, elmnt in enumerate(pkey_values_list) if idx % 2 != 0]

            kwargs.update({
                'p[0]': operation + "|" + pk_item1 + "|" + "|".join(str(recnum) for recnum in recnum_list),
                'p[1]': operation + "|" + pk_item2 + "|" + "|".join(str(series) for series in series_name_list)
            })

        # Primary_key is like : recnum
        elif len(pk_item_component) == 1:
            resources_list = []
            if plugin_name is None:
                raise ValueError("Error execute_plugin():\nNo plugin_name provided\n")
            for resource in self.resources_target:
                resources_list.append(resource.split("/")[-1])
            if plugin_name not in resources_list:
                raise ValueError("Error execute_plugin():\n This plugin_name %s does not exist in %s dataset\n" %
                                 (plugin_name, self.name))
            if len(pkey_values_list) == 0:
                raise ValueError("Error execute_plugin():\nNo identifiers pkey provided\n")
            if filename is None:
                raise ValueError("Error execute_plugin():\nNo filename provided\n")
            operation = 'LISTBOXMULTIPLE'
            kwargs.update({
                'p[0]': operation + "|" + self.primary_key.name + "|" + "|".join(
                    str(pkey_value) for pkey_value in pkey_values_list)
            })

        url = self.url + "/" + plugin_name + "?archiveType=" + self.download_type.lower() + "&" + urlencode(kwargs)

        try:
            urlopen(url)
        except HTTPError as e:
            print("code error :%s" % e.code)
            print("Reason : %s " % e.reason)
            raise
        except Exception as e:
            print(e.args)
            raise
        else:
            return urlretrieve('%s' % url, filename)
