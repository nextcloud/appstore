App Developer Guide
===================

Most of today's developers publish their source code on GitHub, BitBucket or on their own GitLab instance. These tools typically also provide a way to release new versions based on Git tags or by uploading custom archives.

Advanced users and developers typically prefer to download the app directly from these services whereas administrators or novice users look for app releases on the app store. This means that you have to take care of publishing two releases on two different platforms.

We want to avoid duplication and make it harder to ship broken releases by mistake, therefore we went for the following solution:

* Your app's source code is hosted on GitHub or a similar service

* You should use Git tags to create new releases on these services

* Archives are typically created automatically for you. If you require compilation or other transformations like minification, you should upload a pre-built archive to the appropriate releases page

This keeps your repository up to date and satisfies the needs of developers and advanced users.

App Release Workflow
--------------------

To publish an app release on the app store you simply send us a download link for the release archive using either :doc:`ncdev <ncdev>` or any tool that can access the :doc:`restapi` (even with curl). We then do the following:

* Your archive is downloaded from the given location. This ensures that your users don't hit dead links. If your archive is too big, we will abort the download.

* The archive is then extracted and the package structure is validated:

 * The archive most only contain one top level folder consisting of lower case ASCII characters and underscores
 * The archive must contain an **info.xml** file inside the **appinfo** directory which in turn is located in the top folder

* The app's metadata is then extracted from the **info.xml** file

* The info.xml is reformatted using XSLT to bring everything into the correct order (required for XSD 1.0) and unknown elements are dropped

* The cleaned up info.xml is then validated using an XML Schema (see :ref:`info-schema`)

* The release is then either created or updated. The downloaded archive will be deleted

.. _info-schema:

Schema Integration
------------------
We provide an XML schema for the info.xml file which is available under `https://apps.nextcloud.com/schema/apps/info.xsd <https://apps.nextcloud.com/schema/apps/info.xsd>`_ and can be used to validate your info.xml or provide autocompletion in your IDE.

You can validate your info.xml using `various online tools <http://www.utilities-online.info/xsdvalidation/>`_

Various IDEs automatically validate and auto complete XML elements and attributes if you add the schema in your info.xml like this:

.. code-block:: xml

    <?xml version="1.0"?>
    <info xmlns:xsi= "http://www.w3.org/2001/XMLSchema-instance"
          xsi:noNamespaceSchemaLocation="https://apps.nextcloud.com/schema/apps/info.xsd">

          <!-- content here -->

    </info>

Verification
------------
Since we don't host the package ourselves this implies that the download location must be trusted. The following mechanisms are in place to guarantee that the downloaded version has not been tampered with:

* You can submit a sha256sum hash in addition to the download link. The hash is validated on the user's server when he installs it. If you omit the hash, we generate it from the downloaded archive

* You can sign your code `using a certificate <https://docs.nextcloud.org/server/9/developer_manual/app/code_signing.html>`_

* You must supply an HTTPS download url for the archive
