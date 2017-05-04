========
Overview
========

*This package is at present not reusable without depending on a large
chunk of the Zope Toolkit and its assumptions. It is maintained by the*
`Zope Toolkit project <http://docs.zope.org/zopetoolkit/>`_.

This package used to provide browser page, resource and menu classes
for use with zope.publisher object publishing framework, as well as some
other useful utilities and adapters, but most of things was factored out
to separate packages, leaving here only backward-compatibility imports.

However, some potentially useful things are still contained in this package:

 * "date" field converter for zope.publisher's BrowserRequest field converter
   mechanism.
 
 * "Browser Skins" vocabulary (a vocabulary for IBrowserSkinType utilities)
 
 * ManagementViewSelector (a browser view that redirects to a first available
   management view)

 * XML-RPC view and method publishing mechanism along with xmlrpc:view ZCML
   directive.
