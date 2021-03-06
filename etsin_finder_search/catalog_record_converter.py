from etsin_finder_search.reindexing_log import get_logger

log = get_logger(__name__)


class CRConverter:

    def convert_metax_cr_json_to_es_data_model(self, metax_cr_json):
        es_dataset = {}
        if metax_cr_json.get('research_dataset', False) and \
                metax_cr_json.get('research_dataset').get('urn_identifier', False):

            m_rd = metax_cr_json['research_dataset']
            es_dataset['urn_identifier'] = m_rd['urn_identifier']
            es_dataset['preferred_identifier'] = m_rd.get('preferred_identifier', '')

            if 'organization_name' not in es_dataset:
                es_dataset['organization_name'] = []

            if metax_cr_json.get('date_modified', False):
                es_dataset['date_modified'] = metax_cr_json.get('date_modified')
            else:
                es_dataset['date_modified'] = metax_cr_json.get('date_created')

            if m_rd.get('title', False):
                es_dataset['title'] = m_rd.get('title')

            if m_rd.get('description', False):
                es_dataset['description'] = m_rd.get('description')

            if m_rd.get('keyword', False):
                es_dataset['keyword'] = m_rd.get('keyword')

            if metax_cr_json.get('preservation_state', False):
                es_dataset['preservation_state'] = metax_cr_json.get('preservation_state')

            for m_other_identifier_item in m_rd.get('other_identifier', []):
                if 'other_identifier' not in es_dataset:
                    es_dataset['other_identifier'] = []

                es_other_identifier = {}

                if m_other_identifier_item.get('notation'):
                    es_other_identifier['notation'] = m_other_identifier_item.get('notation')

                if m_other_identifier_item.get('type', False):
                    es_other_identifier['type'] = {}
                    self._convert_metax_obj_containing_identifier_and_label_to_es_model(
                        m_other_identifier_item.get('type'), es_other_identifier['type'], 'pref_label')

                es_dataset['other_identifier'].append(es_other_identifier)

            if m_rd.get('access_rights', False):
                if 'access_rights' not in es_dataset:
                    es_dataset['access_rights'] = {}

                es_access_rights = es_dataset['access_rights']

                if m_rd.get('access_rights').get('license', False):
                    m_license = m_rd.get('access_rights').get('license')
                    self._convert_metax_obj_containing_identifier_and_label_to_es_model(m_license, es_access_rights,
                                                                                        'title', 'license')

                if m_rd.get('access_rights').get('type', False):
                    m_type = m_rd.get('access_rights').get('type')
                    self._convert_metax_obj_containing_identifier_and_label_to_es_model(m_type, es_access_rights,
                                                                                        'pref_label', 'type')

            if m_rd.get('theme', False):
                if 'theme' not in es_dataset:
                    es_dataset['theme'] = []

                m_theme = m_rd.get('theme')
                self._convert_metax_obj_containing_identifier_and_label_to_es_model(m_theme, es_dataset, 'pref_label',
                                                                                    'theme')

            if m_rd.get('field_of_science', False):
                if 'field_of_science' not in es_dataset:
                    es_dataset['field_of_science'] = []

                m_field_of_science = m_rd.get('field_of_science')
                self._convert_metax_obj_containing_identifier_and_label_to_es_model(m_field_of_science, es_dataset,
                                                                                    'pref_label', 'field_of_science')

            for m_is_output_of_item in m_rd.get('is_output_of', []):
                if 'project' not in es_dataset:
                    es_dataset['project'] = []

                es_project = {}
                self._convert_metax_obj_containing_identifier_and_label_to_es_model(m_is_output_of_item, es_project,
                                                                                    'name')

                if m_is_output_of_item.get('has_funding_agency', []):
                    self._convert_metax_org_or_person_to_es_model(m_is_output_of_item.get('has_funding_agency'),
                                                                  es_project, 'has_funding_agency')
                    self._convert_metax_organization_name_to_es_model(m_is_output_of_item.get('has_funding_agency'), es_dataset, 'organization_name')

                if m_is_output_of_item.get('source_organization', []):
                    self._convert_metax_org_or_person_to_es_model(m_is_output_of_item.get('source_organization'),
                                                                  es_project, 'source_organization')
                    self._convert_metax_organization_name_to_es_model(m_is_output_of_item.get('source_organization'), es_dataset, 'organization_name')

                es_dataset['project'].append(es_project)

            if m_rd.get('contributor', False):
                es_dataset['contributor'] = []
                self._convert_metax_org_or_person_to_es_model(m_rd.get('contributor'), es_dataset, 'contributor')
                self._convert_metax_organization_name_to_es_model(m_rd.get('contributor'), es_dataset, 'organization_name')

            if m_rd.get('publisher', False):
                es_dataset['publisher'] = []
                self._convert_metax_org_or_person_to_es_model(m_rd.get('publisher'), es_dataset, 'publisher')
                self._convert_metax_organization_name_to_es_model(m_rd.get('publisher'), es_dataset, 'organization_name')

            if m_rd.get('curator', False):
                es_dataset['curator'] = []
                self._convert_metax_org_or_person_to_es_model(m_rd.get('curator'), es_dataset, 'curator')
                self._convert_metax_organization_name_to_es_model(m_rd.get('curator'), es_dataset, 'organization_name')

            if m_rd.get('creator', False):
                es_dataset['creator'] = []
                self._convert_metax_org_or_person_to_es_model(m_rd.get('creator'), es_dataset, 'creator')
                self._convert_metax_creator_name_to_es_model(m_rd.get('creator'), es_dataset, 'creator_name')
                self._convert_metax_organization_name_to_es_model(m_rd.get('creator'), es_dataset, 'organization_name')

            if m_rd.get('rights_holder', False):
                es_dataset['rights_holder'] = []
                self._convert_metax_org_or_person_to_es_model(m_rd.get('rights_holder'), es_dataset, 'rights_holder')
                self._convert_metax_organization_name_to_es_model(m_rd.get('rights_holder'), es_dataset, 'organization_name')

        return es_dataset

    @staticmethod
    def _convert_metax_obj_containing_identifier_and_label_to_es_model(m_input, es_output, m_input_label_field,
                                                                       es_array_relation_name=''):
        """

        If m_input is not array, set identifier and label directly on es_output.
        If m_input is array, add a es_array_relation_name array relation to es_output, which will contain objects
        having identifier and label each

        :param m_input:
        :param es_output:
        :param m_input_label_field:
        :param es_array_relation_name:
        :return:
        """

        if isinstance(m_input, list) and es_array_relation_name:
            output = []
            for obj in m_input:
                m_input_label_is_array = isinstance(obj.get(m_input_label_field), list)
                out_obj = {
                    'identifier': obj.get('identifier', ''),
                    m_input_label_field: obj.get(m_input_label_field, [] if m_input_label_is_array else {})
                }
                output.append(out_obj)
            es_output[es_array_relation_name] = output
        elif isinstance(m_input, dict):
            m_input_label_is_array = isinstance(m_input.get(m_input_label_field), list)
            es_output['identifier'] = m_input.get('identifier', '')
            es_output[m_input_label_field] = m_input.get(m_input_label_field, [] if m_input_label_is_array else {})

    def _convert_metax_org_or_person_to_es_model(self, m_input, es_output, relation_name):
        """

        :param m_input:
        :param es_output:
        :param relation_name:
        :return:
        """

        if isinstance(m_input, list):
            output = []
            for m_obj in m_input:
                output.append(self._get_converted_single_org_or_person_es_model(m_obj))
        else:
            output = {}
            if m_input:
                output = self._get_converted_single_org_or_person_es_model(m_input)

        es_output[relation_name] = output

    def _convert_metax_creator_name_to_es_model(self, m_input, es_output, relation_name):
        """

        :param m_input:
        :param es_output:
        :param relation_name:
        :return:
        """

        output = []
        if isinstance(m_input, list):
            for m_obj in m_input:
                name = self._get_converted_creator_name_es_model(m_obj)
                if name is not None:
                    output.extend(name)
        else:
            if m_input:
                output = self._get_converted_creator_name_es_model(m_input)

        es_output[relation_name] = output

    def _convert_metax_organization_name_to_es_model(self, m_input, es_output, relation_name):
        """

        :param m_input:
        :param es_output:
        :param relation_name:
        :return:
        """

        output = []
        if isinstance(m_input, list):
            for m_obj in m_input:
                name = self._get_converted_organization_name_es_model(m_obj)
                if name is not None:
                    output.extend(name)
                if 'is_part_of' in m_obj:
                    self._convert_metax_organization_name_to_es_model(m_obj['is_part_of'], es_output, relation_name)
                if 'member_of' in m_obj:
                    self._convert_metax_organization_name_to_es_model(m_obj['member_of'], es_output, relation_name)
        else:
            if m_input:
                output = self._get_converted_organization_name_es_model(m_input)
                if 'is_part_of' in m_input:
                    self._convert_metax_organization_name_to_es_model(m_input['is_part_of'], es_output, relation_name)
                if 'member_of' in m_input:
                    self._convert_metax_organization_name_to_es_model(m_input['member_of'], es_output, relation_name)

        if output is not None:
            es_output[relation_name].extend(output)

    def _get_converted_single_org_or_person_es_model(self, m_obj):
        if m_obj.get('@type', '') not in ['Person', 'Organization']:
            return None

        out_obj = self._get_es_person_or_org_common_data_from_metax_obj(m_obj)

        agent_type = m_obj.get('@type')
        if agent_type == 'Person' and m_obj.get('member_of', False):
            out_obj.update(
                {'belongs_to_org': self._get_es_person_or_org_common_data_from_metax_obj(m_obj.get('member_of'))})
        elif agent_type == 'Organization' and m_obj.get('is_part_of', False):
            out_obj.update(
                {'belongs_to_org': self._get_es_person_or_org_common_data_from_metax_obj(m_obj.get('is_part_of'))})

        return out_obj

    def _get_converted_creator_name_es_model(self, m_obj):
        if m_obj.get('@type', '') not in ['Person', 'Organization']:
            return None

        person_or_org = self._get_es_person_or_org_common_data_from_metax_obj(m_obj)
        out_obj = list(person_or_org['name'].values())

        return out_obj

    def _get_converted_organization_name_es_model(self, m_obj):
        if m_obj.get('@type', '') != 'Organization':
            return None

        org = self._get_es_person_or_org_common_data_from_metax_obj(m_obj)
        out_obj = list(org['name'].values())
        out_obj = [x for x in out_obj if x] # remove empty strings

        return out_obj

    @staticmethod
    def _get_es_person_or_org_common_data_from_metax_obj(m_obj):
        # Name should be langstring
        name = m_obj.get('name', '')
        if not isinstance(m_obj.get('name'), dict):
            name = {'und': m_obj.get('name', '')}

        return {
            'identifier': m_obj.get('identifier', ''),
            'name': name,
            'agent_type': m_obj.get('@type')
        }
