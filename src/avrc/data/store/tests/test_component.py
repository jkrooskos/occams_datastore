#    def test_multi_site(self):
#        """ Test that the DataStore is able to handle being added to multiple
#            sites without mixing the underlying database engines and session.
#        """
#
#        root = rootFolder()
#
#        root[u"site1"] = site1 = SiteManagerContainer()
#        root[u"site2"] = site2 = SiteManagerContainer()
#
#        self.assertNotEqual(site1, site2, u"Site containers must be different.")
#
#        site1.setSiteManager(LocalSiteManager(site1))
#        site2.setSiteManager(LocalSiteManager(site2))
#
#        sm1 = site1.getSiteManager()
#        sm2 = site2.getSiteManager()
#
#        self.assertNotEqual(sm1, sm2, u"Site managers must be different.")
#
#        sm1.registerUtility(component=datastore.Datastore(
#                                  title=u"ds1",
#                                  dsn=u"sqlite:///:memory:"),
#                            provided=interfaces.IDatastore)
#        sm2.registerUtility(component=datastore.Datastore(
#                                  title=u"ds2",
#                                  dsn=u"sqlite:///:memory:"),
#                            provided=interfaces.IDatastore)
#
#        setSite(site1)
#        ds1 = getUtility(interfaces.IDatastore)
#
#        setSite(site2)
#        ds2 = getUtility(interfaces.IDatastore)
#
#        self.assertNotEqual(ds1, ds2)
#
#        setSite(site1)
#        ds = getUtility(interfaces.IDatastore)
#        Session = named_session(ds)
#        session = Session()
#
#        session.add(model.Type(title=u"FOO"))
#        session.commit()
#
#        p = session.query(model.Type).filter_by(title=u"FOO").first()
#        self.assertTrue(p is not None, "No person found in first database")
#
#        p = session.query(model.Type).filter_by(title=u"BAR").first()
#        self.assertTrue(p is None, "Databases engines are mixed up.")
#
#        setSite(site2)
#        ds = getUtility(interfaces.IDatastore)
#        Session = named_session(ds)
#        session = Session()
#
#        session.add(model.Type(title=u"BAR"))
#        session.commit()
#
#        p = session.query(model.Type).filter_by(title=u"BAR").first()
#        self.assertTrue(p is not None, "No person found in first database")
#
#        p = session.query(model.Type).filter_by(title=u"FOO").first()
#        self.assertTrue(p is None, "Databases engines are mixed up.")