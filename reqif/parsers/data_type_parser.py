from typing import Union, Optional, List

from lxml import etree

from reqif.helpers.lxml import is_self_closed_tag
from reqif.models.reqif_data_type import (
    ReqIFDataTypeDefinitionString,
    ReqIFDataTypeDefinitionEnumeration,
    ReqIFDataTypeDefinitionInteger,
    ReqIFEnumValue,
    ReqIFDataTypeDefinitionXHTML,
    ReqIFDataTypeDefinitionDate,
    ReqIFDataTypeDefinitionReal,
)


class DataTypeParser:
    @staticmethod
    def parse(
        data_type_xml,
    ) -> Union[
        ReqIFDataTypeDefinitionString,
        ReqIFDataTypeDefinitionInteger,
        ReqIFDataTypeDefinitionEnumeration,
        ReqIFDataTypeDefinitionXHTML,
        ReqIFDataTypeDefinitionDate,
        ReqIFDataTypeDefinitionReal,
    ]:
        assert "DATATYPE-DEFINITION-" in data_type_xml.tag, f"{data_type_xml}"

        is_self_closed = is_self_closed_tag(data_type_xml)

        attributes = data_type_xml.attrib
        identifier = attributes["IDENTIFIER"]
        last_change = (
            attributes["LAST-CHANGE"] if "LAST-CHANGE" in attributes else None
        )
        long_name = (
            attributes["LONG-NAME"] if "LONG-NAME" in attributes else None
        )

        description = attributes["DESC"] if "DESC" in attributes else None

        if data_type_xml.tag == "DATATYPE-DEFINITION-ENUMERATION":
            multi_valued_string = (
                attributes["MULTI-VALUED"]
                if "MULTI-VALUED" in attributes
                else None
            )
            multi_valued = (
                multi_valued_string == "true" if multi_valued_string else None
            )
            values: Optional[List[ReqIFEnumValue]] = None
            xml_specified_values = data_type_xml.find("SPECIFIED-VALUES")
            if xml_specified_values is not None:
                values = []
                for xml_specified_value in xml_specified_values:
                    specified_value_attributes = xml_specified_value.attrib
                    specified_value_identifier = specified_value_attributes[
                        "IDENTIFIER"
                    ]
                    specified_value_description = (
                        specified_value_attributes["DESC"]
                        if "DESC" in specified_value_attributes
                        else None
                    )
                    specified_value_last_change: Optional[str] = (
                        specified_value_attributes["LAST-CHANGE"]
                        if "LAST-CHANGE" in specified_value_attributes
                        else None
                    )
                    specified_value_long_name: Optional[str] = (
                        specified_value_attributes["LONG-NAME"]
                        if "LONG-NAME" in specified_value_attributes
                        else None
                    )
                    properties = xml_specified_value.find("PROPERTIES")

                    embedded_value = properties.find("EMBEDDED-VALUE")
                    embedded_value_attributes = embedded_value.attrib

                    embedded_value_key = embedded_value_attributes["KEY"]
                    embedded_value_other_content = (
                        embedded_value_attributes["OTHER-CONTENT"]
                        if "OTHER-CONTENT" in embedded_value_attributes
                        else None
                    )
                    values.append(
                        ReqIFEnumValue(
                            description=specified_value_description,
                            identifier=specified_value_identifier,
                            last_change=specified_value_last_change,
                            key=embedded_value_key,
                            other_content=embedded_value_other_content,
                            long_name=specified_value_long_name,
                        )
                    )
            return ReqIFDataTypeDefinitionEnumeration(
                is_self_closed=is_self_closed,
                description=description,
                identifier=identifier,
                last_change=last_change,
                long_name=long_name,
                multi_valued=multi_valued,
                values=values,
            )

        if data_type_xml.tag == "DATATYPE-DEFINITION-STRING":
            max_length = (
                attributes["MAX-LENGTH"] if "MAX-LENGTH" in attributes else None
            )

            return ReqIFDataTypeDefinitionString(
                is_self_closed=is_self_closed,
                description=description,
                identifier=identifier,
                last_change=last_change,
                long_name=long_name,
                max_length=max_length,
            )

        if data_type_xml.tag == "DATATYPE-DEFINITION-INTEGER":
            return ReqIFDataTypeDefinitionInteger(
                description=description,
                identifier=identifier,
                last_change=last_change,
                long_name=long_name,
            )

        if data_type_xml.tag == "DATATYPE-DEFINITION-XHTML":
            return ReqIFDataTypeDefinitionXHTML(
                is_self_closed=is_self_closed,
                description=description,
                identifier=identifier,
                last_change=last_change,
                long_name=long_name,
            )

        # TODO: All the following is parsed to just String.
        if data_type_xml.tag == "DATATYPE-DEFINITION-BOOLEAN":
            return ReqIFDataTypeDefinitionString(
                is_self_closed=False,
                description=description,
                identifier=identifier,
                last_change=last_change,
                long_name=long_name,
                max_length=None,
            )

        if data_type_xml.tag == "DATATYPE-DEFINITION-REAL":     
            accuracy = (
                attributes["ACCURACY"] if "ACCURACY" in attributes else None
            )
            max_value = (
                attributes["MAX-VALUE"] if "MAX-VALUE" in attributes else None
            )
            min_value = (
                attributes["MIN-VALUE"] if "MIN-VALUE" in attributes else None
            )
            return ReqIFDataTypeDefinitionReal(
                description=description,
                identifier=identifier,
                last_change=last_change,
                long_name=long_name,
                accuracy=accuracy,
                max_value=max_value,
                min_value=min_value,
            )

        if data_type_xml.tag == "DATATYPE-DEFINITION-DATE":
            return ReqIFDataTypeDefinitionDate(
                description=description,
                identifier=identifier,
                last_change=last_change,
                long_name=long_name,
            )

        raise NotImplementedError(etree.tostring(data_type_xml))

    @staticmethod
    def unparse(
        data_type_definition: Union[
            ReqIFDataTypeDefinitionString, ReqIFDataTypeDefinitionEnumeration
        ]
    ) -> str:
        if isinstance(data_type_definition, ReqIFDataTypeDefinitionString):
            output = "        <DATATYPE-DEFINITION-STRING"
            if data_type_definition.description:
                output += f' DESC="{data_type_definition.description}"'

            output += f' IDENTIFIER="{data_type_definition.identifier}"'
            if data_type_definition.last_change:
                output += f' LAST-CHANGE="{data_type_definition.last_change}"'
            if data_type_definition.long_name:
                output += f' LONG-NAME="{data_type_definition.long_name}"'
            if data_type_definition.max_length:
                output += f' MAX-LENGTH="{data_type_definition.max_length}"'
            if data_type_definition.is_self_closed:
                output += "/>\n"
            else:
                output += ">\n"
                output += "        </DATATYPE-DEFINITION-STRING>\n"
            return output
        if isinstance(data_type_definition, ReqIFDataTypeDefinitionInteger):
            output = "        <DATATYPE-DEFINITION-INTEGER"
            if data_type_definition.description:
                output += f' DESC="{data_type_definition.description}"'

            output += f' IDENTIFIER="{data_type_definition.identifier}"'
            if data_type_definition.last_change:
                output += f' LAST-CHANGE="{data_type_definition.last_change}"'
            if data_type_definition.long_name:
                output += f' LONG-NAME="{data_type_definition.long_name}"'
            output += "/>\n"
            return output
        if isinstance(data_type_definition, ReqIFDataTypeDefinitionEnumeration):
            output = "        <DATATYPE-DEFINITION-ENUMERATION"
            if data_type_definition.description:
                output += f' DESC="{data_type_definition.description}"'

            output += f' IDENTIFIER="{data_type_definition.identifier}"'
            if data_type_definition.last_change:
                output += f' LAST-CHANGE="{data_type_definition.last_change}"'
            if data_type_definition.long_name:
                output += f' LONG-NAME="{data_type_definition.long_name}"'
            if data_type_definition.is_self_closed:
                output += "/>\n"
            else:
                output += ">\n"

            if data_type_definition.values is not None:
                output += "          <SPECIFIED-VALUES>\n"

                for value in data_type_definition.values:
                    output += "            <ENUM-VALUE"
                    if value.description is not None:
                        output += f' DESC="{value.description}"'
                    output += f' IDENTIFIER="{value.identifier}"'
                    if value.last_change is not None:
                        output += f' LAST-CHANGE="{value.last_change}"'
                    if value.long_name is not None:
                        output += f' LONG-NAME="{value.long_name}"'
                    output += ">\n"

                    output += "              <PROPERTIES>\n"
                    output += (
                        "                " f'<EMBEDDED-VALUE KEY="{value.key}"'
                    )
                    if value.other_content is not None:
                        output += f' OTHER-CONTENT="{value.other_content}"'
                    output += " />\n"
                    output += "              </PROPERTIES>\n"

                    output += "            </ENUM-VALUE>\n"

                output += "          </SPECIFIED-VALUES>\n"

            if not data_type_definition.is_self_closed:
                output += "        </DATATYPE-DEFINITION-ENUMERATION>\n"
            return output

        if isinstance(data_type_definition, ReqIFDataTypeDefinitionXHTML):
            output = "        <DATATYPE-DEFINITION-XHTML"
            if data_type_definition.description:
                output += f' DESC="{data_type_definition.description}"'

            output += f' IDENTIFIER="{data_type_definition.identifier}"'
            if data_type_definition.last_change:
                output += f' LAST-CHANGE="{data_type_definition.last_change}"'
            if data_type_definition.long_name:
                output += f' LONG-NAME="{data_type_definition.long_name}"'
            if data_type_definition.is_self_closed:
                output += "/>\n"
            else:
                output += ">\n"
                output += "        </DATATYPE-DEFINITION-XHTML>\n"
            return output

        if isinstance(data_type_definition, ReqIFDataTypeDefinitionReal):
            output = "        <DATATYPE-DEFINITION-REAL"
            if data_type_definition.description:
                output += f' DESC="{data_type_definition.description}"'

            output += f' IDENTIFIER="{data_type_definition.identifier}"'
            if data_type_definition.last_change:
                output += f' LAST-CHANGE="{data_type_definition.last_change}"'
            if data_type_definition.long_name:
                output += f' LONG-NAME="{data_type_definition.long_name}"'
            if data_type_definition.max_length:
                output += f' MAX-LENGTH="{data_type_definition.max_length}"'
            if data_type_definition.accuracy:
                output += f' ACCURACY="{data_type_definition.accuracy}"'
            if data_type_definition.max_value:
                output += f' MAX-VALUE="{data_type_definition.max_value}"'
            if data_type_definition.min_value:
                output += f' MIN-VALUE="{data_type_definition.min_value}"'
            if data_type_definition.is_self_closed:
                output += "/>\n"
            else:
                output += ">\n"
                output += "        </DATATYPE-DEFINITION-REAL>\n"
            return output

        if isinstance(data_type_definition, ReqIFDataTypeDefinitionDate):
                    output = "        <DATATYPE-DEFINITION-DATE"
                    if data_type_definition.description:
                        output += f' DESC="{data_type_definition.description}"'

                    output += f' IDENTIFIER="{data_type_definition.identifier}"'
                    if data_type_definition.last_change:
                        output += f' LAST-CHANGE="{data_type_definition.last_change}"'
                    if data_type_definition.long_name:
                        output += f' LONG-NAME="{data_type_definition.long_name}"'
                    output += "/>\n"
                    return output

        raise NotImplementedError(data_type_definition) from None
