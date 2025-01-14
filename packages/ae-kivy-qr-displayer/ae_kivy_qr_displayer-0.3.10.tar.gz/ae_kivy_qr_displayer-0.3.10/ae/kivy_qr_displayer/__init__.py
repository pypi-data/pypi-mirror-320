"""
qr code displayer widget
========================

the popup widget :class:`QrDisplayerPopup` provided by this ae namespace portion is displaying QR codes.

the :class:`QrDisplayerPopup` is inherited from :class:`ae.kivy.widgets.FlowPopup` and is embedding the Kivy Garden
:mod:`kivy_garden.qrcode` module.

qr displayer popup usage
------------------------

to display a QR code instantiate :class:`QrDisplayerPopup` specifying in the `title` property of the popup the string to
encode to a QR image and in the `qr_content` property a short string describing the content of the string to encode.
after that call the `open` method::

    qr_displayer = QrDisplayerPopup(title="string to encode", qr_content="what to encode")
    qr_displayer.open()

alternatively you can simply :meth:`change the application flow <ae.gui_app.change_flow>` to
`id_of_flow('open', 'qr_displayer')` (see also :ref:`application flow`)::

     main_app.change_flow(id_of_flow('open', 'qr_displayer'),
                          popup_kwargs=dict(title="string to encode",
                                            qr_content="what to encode"))

the label texts used by this popup widget are automatically translated into the german and spanish language via the
translation texts provided in the resources of this ae namespace portion.

.. note::
    if your app is providing i18n translations then the `qr_content` string has to be translated (e.g. by using
    :meth:`~ae.kivy.i18n.get_txt` or :meth:`~ae.i18n.get_text`) before it gets passed to the popup kwargs.

to support additional languages simply add the translations texts to your app's translation texts resources or submit a
PR to add them to this ae namespace portion. alternatively you could put different wording by specifying also the
english translation text.

.. hint::
    apart from `root.qr_content` you can also use `root.title` in the translation texts to repeat/mention the string to
    encode in the text content.
"""
from kivy.lang import Builder                       # type: ignore
from kivy.properties import StringProperty          # type: ignore # pylint: disable=no-name-in-module

# noinspection PyUnresolvedReferences
from kivy_garden.qrcode import QRCodeWidget         # type: ignore # noqa: F401

from ae.i18n import register_package_translations   # type: ignore
from ae.kivy.widgets import FlowPopup               # type: ignore


__version__ = '0.3.10'


register_package_translations()

Builder.load_string('''\
<QrDisplayerPopup>
    title: "string to codify"
    query_data_maps:
        [dict(cls='QRCodeWidget', kwargs=dict(
        data=root.title,
        size_hint=(1, 1),
        size_hint_min=(sp(300), sp(300)),
        size_hint_max=(sp(600), sp(600)),
        ))]
    optimal_content_width: root._max_width / (2.1 if app.landscape else 0.99)
    optimal_content_height: max(c_text.height, root.ids.query_box.height) if app.landscape else c_text.height
    ImageLabel:
        id: c_text
        text:
            # duplicate backslash (in \\n) prevents Kivy rule parsing exception
            _("The displayed QR code contains the [b]{root.qr_content}[/b] shown in the window title.") \
            + _("\\nEither copy manually the window title string or use a QR code reader.") \
            + _("\\n\\nTap outside of this window to close it.")
        text_size: root.optimal_content_width - self.padding[0] * 2.1, None
        size_hint_y: None
        height: self.texture_size[1]
        padding: sp(18), sp(9)
''')


class QrDisplayerPopup(FlowPopup):
    """ qr code displayer. """
    qr_content = StringProperty()       #: string to name the content that get displayed as QR code
