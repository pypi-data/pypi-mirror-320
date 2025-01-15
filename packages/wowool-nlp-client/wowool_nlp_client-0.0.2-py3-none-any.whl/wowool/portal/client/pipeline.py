import logging
from typing import List, Union

from wowool.document import Document
from requests.exceptions import ReadTimeout

from wowool.io.provider import InputProvider
from wowool.portal.client.error import ClientError
from wowool.portal.client.httpcode import HttpCode
from wowool.portal.client.portal import Portal, _PortalMixin

logger = logging.getLogger(__name__)

PLK_DATA = "data"


def _to_document(data: Union[str, dict, InputProvider], id: str) -> dict:
    if isinstance(data, str):
        return {"id": str(id), PLK_DATA: data}
    elif isinstance(data, dict):
        if not ("id" in data and PLK_DATA in data):
            raise ClientError("Missing required 'id' and 'data' fields")
        return data
    elif isinstance(data, Document) or isinstance(data, InputProvider):
        return {"id": data.id, PLK_DATA: data.text}

    raise ClientError(f"Invalid data type '{type(data)}'")


def _to_documents(data: Union[str, dict, InputProvider, list], id: str) -> List[dict]:
    if isinstance(data, list):
        return [_to_document(item, id) for item in data]
    else:
        return [_to_document(data, id)]


class Pipeline(_PortalMixin):
    """
    :class:`Pipeline` is a class used to process your documents.
    """

    def __init__(self, name: str, portal: Portal = None, description=None, **kwargs):
        """
        Initialize a Pipeline instance

        :param name: Name of the Pipeline
        :type name: ``str``
        :param portal: Connection to the Portal server
        :type portal: :class:`Portal`

        :return: An initialized pipeline
        :rtype: :class:`Pipeline`

        .. note::
            If the given name does not exist, the Portal will try to generate one for you. For example, if the provided name is ``english,sentiment`` it will run the English language and ``english-sentiment`` domain
        """
        super(Pipeline, self).__init__(portal)
        self.name = name
        self.description = description
        self.meta = kwargs

    def process_bulk(self, data: Union[str, dict, Document, InputProvider, list], id: str = None, **kwargs) -> List[Document]:
        """
        Functor to process one or more documents. For example:

        .. literalinclude:: init_pipeline_context.py
            :language: python

        :param data: Input data to process. This includes support for one of the :ref:`InputProviders <py_eot_wowool_io_input_providers>`
        :type data: Either a ``str``, ``dict``, :class:`Document <wowool.document.Document>`, :class:`InputProvider <wowool.io.InputProvider>` or a ``list`` of one of the former
        :param id: The ID you wish to associate with each document. By default, if a file is passed, the file's name is used. Similarly, if a string is passed, a hash of the string is used
        :type id: ``str``
        :param kwargs: additional kwargument for the requests library

        :return: A ``list`` of :class:`Document <wowool.document.Document>` instances is returned.
        """

        try:
            assert self.portal, "Portal not passed and not available from context"
            payload = self.portal._service.post(
                url="/nlp/v1/pipeline/run",
                status_code=HttpCode.OK,
                data={
                    "apiKey": self.portal.api_key,
                    "pipeline": self.name,
                    "documents": _to_documents(data, id),
                },
                **kwargs,
            )

            if not payload or "documents" not in payload:
                raise ClientError("Portal returned an invalid response")

            documents = [Document.from_json(document_json) for document_json in payload["documents"]]
            return documents
        except ReadTimeout as ex:
            raise ClientError(str(ex))

    def process(
        self,
        data: Union[str, dict, Document],
        id: str = None,
        **kwargs,
    ) -> Document:
        """
        Functor to process one document. For example:

        .. literalinclude:: init_pipeline_context.py
            :language: python

        :param data: Input data to process. This includes support for one of the :ref:`InputProviders <py_eot_wowool_io_input_providers>`
        :type data: Either a ``str``, ``dict``, :class:`Document <wowool.document.Document>`, :class:`InputProvider <wowool.io.InputProvider>`
        :param id: The ID you wish to associate with the document. By default, if a file is passed, the file's name is used. Similarly, if a string is passed, a hash of the string is used
        :type id: ``str``
        :param kwargs: additional kwargument for the requests library


        :return: :class:`Document <wowool.document.Document>` an instance is returned
        """

        documents = self.process_bulk(data, id, **kwargs)
        assert len(documents) == 1
        return documents[0]

    def __call__(self, data: Union[str, dict, Document, InputProvider], id: str = None, **kwargs) -> Document:
        """
        Functor to process one document. For example:

        .. literalinclude:: init_pipeline_context.py
            :language: python

        :param data: Input data to process. This includes support for one of the :ref:`InputProviders <py_eot_wowool_io_input_providers>`
        :type data: Either a ``str``, ``dict``, :class:`Document <wowool.document.Document>`, :class:`InputProvider <wowool.io.InputProvider>`
        :param id: The ID you wish to associate with the document. By default, if a file is passed, the file's name is used. Similarly, if a string is passed, a hash of the string is used
        :type id: ``str``
        :param kwargs: additional kwargument for the requests library


        :return: :class:`Document <wowool.document.Document>` an instance is returned
        """
        return self.process(data, id, **kwargs)

    def __eq__(self, other):
        is_same_type = Pipeline is type(other)
        is_same_name = self.name == other.name
        return is_same_type and is_same_name

    def __repr__(self):
        return f"""wowool.portal.client.pipeline.Pipeline(name="{self.name}")"""
