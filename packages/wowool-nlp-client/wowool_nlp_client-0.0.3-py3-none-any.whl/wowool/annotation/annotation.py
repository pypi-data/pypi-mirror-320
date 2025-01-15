class BasicAnnotation:
    """
    :class:`BasicAnnotation` is the base class for all annotations
    """

    __slott__ = ["begin_offset", "end_offset"]

    def __init__(self, begin_offset: int, end_offset: int):
        """
        Initialize an :class:`BasicAnnotation` instance

        :param begin_offset: Begin offset of the annotation
        :type begin_offset: ``int``
        :param end_offset: End offset of the annotation
        :type end_offset: ``int``

        :rtype: :class:`BasicAnnotation`
        """
        self._begin_offset: int = begin_offset
        self._end_offset: int = end_offset

    def __repr__(self):
        return "({:>3},{:>3})".format(self.begin_offset, self.end_offset)

    @property
    def begin_offset(self) -> int:
        """
        :return: The begin offset of the annotation
        :type: ``int``
        """
        return self._begin_offset

    @property
    def end_offset(self) -> int:
        """
        :return: The end offset of the annotation
        :type: ``int``
        """
        return self._end_offset

    @property
    def is_concept(self) -> bool:
        """
        :return: Whether the annotation is a :class:`Concept`
        :rtype: ``bool``
        """
        from wowool.annotation.concept import Concept

        return isinstance(self, Concept)

    @property
    def is_sentence(self) -> bool:
        """
        :return: Whether the annotation is a :class:`Sentence`
        :rtype: ``bool``
        """
        from wowool.annotation.sentence import Sentence

        return isinstance(self, Sentence)

    @property
    def is_token(self) -> bool:
        """
        :return: Whether the annotation is a :class:`Token`
        :rtype: ``bool``
        """
        from wowool.annotation.token import Token

        return isinstance(self, Token)

    @property
    def is_paragraph(self) -> bool:
        """
        :return: Whether the annotation is a :class:`Paragraph`
        :rtype: ``bool``
        """
        from wowool.annotation.paragraph import Paragraph

        return isinstance(self, Paragraph)


class Annotation(BasicAnnotation):
    """
    :class:`Annotation` is the base class for all annotations
    """

    __slott__ = ["begin_offset", "end_offset"]

    def __init__(self, begin_offset: int, end_offset: int):
        """
        Initialize an :class:`Annotation` instance

        :param begin_offset: Begin offset of the annotation
        :type begin_offset: ``int``
        :param end_offset: End offset of the annotation
        :type end_offset: ``int``

        :rtype: :class:`Annotation`
        """
        super(Annotation, self).__init__(begin_offset, end_offset)
        self._annotation_idx = None

    @property
    def index(self) -> int:
        assert self._annotation_idx != None
        return self._annotation_idx


class ErrorAnnotationNotFound(ValueError):
    pass
