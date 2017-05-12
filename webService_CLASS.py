# -*- coding: utf-8 -*-
"""
/***************************************************************************

Definition of the web-service object
All the properties required to call a web-service
"""



class WebServiceParams:
	
    def __init__(self, name, nameGr,nameEn,sourceGR,sourceEN,creationDate,
                 lastUpdate,descEN,descGR,serviceType, layerName,server,
                 QLname,crc,bbox,country,city,mapType,typeDisaster,mapFormat):
        self.name = name
        self.nameGr = nameGr
    	self.nameEn = nameEn
    	self.creationDate = creationDate
    	self.lastUpdate = lastUpdate
        self.sourceGR = sourceGR
        self.sourceEN = sourceEN
        self.descGR = descGR
        self.descEN = descEN
        self.serviceType = serviceType
        self.layerName = layerName
        self.server = server
        self.QLname= QLname
        self.crc=crc
        self.bbox=bbox
        self.country=country
        self.city=city
        self.mapType=mapType
        self.typeDisaster=typeDisaster
        self.mapFormat=mapFormat

    def getName(self, language):
        # check the language
        if language == "EN":
            name = self.nameEn
        elif language == "GR":
            name = self.nameGr
        # encode to utf-8
        name = unicode(name, 'utf-8')
        return name        

    def getSource(self, language):
        # check the language
        if language == "EN":
            src = self.sourceEN
        elif language == "GR":
            src = self.sourceGR
        # encode to utf-8
        src = unicode(src, 'utf-8')
        return src
        

    def getDescription(self, language):
        # check the language
        if language == "EN":
            desc = self.descEN            
        elif language == "GR":
            desc = self.descGR
        # encode to utf-8
        desc = unicode(desc, 'utf-8')
        return desc

    def getCountry(self, language):
        # check the language
        country = self.country            
        country = unicode(country, 'utf-8')
        return country 

    def getTypeDisaster(self):
        # check the language
        typeDisaster = self.typeDisaster            
        typeDisaster = unicode(typeDisaster, 'utf-8')
        return typeDisaster        
		
    def webServiceParams(self):

        if self.serviceType == "WMS":          
        
            ignoreRequests = "IgnoreGetFeatureInfoUrl=1&IgnoreGetMapUrl=1&"              
            layers = "&layers="+self.layerName
            styles = "&styles="
            url = "&url=" + self.server +"?"
            '''
            EPSG = "EPSG:2100"
            if "gis.ktimanet.gr" in url:
                EPSG = "EPSG:4326"
            elif "ims.geoinfo.ait.ac.th" in url:
                EPSG = "EPSG:4326"    
            '''
            EPSG = self.crc
            params = "contextualWMSLegend=0&crs=" + EPSG+"&dpiMode=7&featureCount=10&format=image/png"
            #construct url to call the webService
            urlWithParams = ignoreRequests + params + layers +  styles +  url

            return  urlWithParams
        
        elif self.serviceType == "WFS":
            url = self.server + "?"
            getFeatureRequest = "SERVICE=WFS&VERSION=1.0.0&REQUEST=GetFeature"
            layer = "&TYPENAME="+ self.layerName
            EPSG = "&SRSNAME="+self.crc

            urlWithParams = url + getFeatureRequest + layer + EPSG
            return  urlWithParams

        elif self.serviceType == "WCS":
            url = self.server + "?"
            getFeatureRequest = "SERVICE=WCS&VERSION=1.0.0&REQUEST=GetCoverage&FORMAT=TIFF&BBOX="+self.bbox+"&WIDTH=512&HEIGHT=512"
            layer = "&COVERAGE="+ self.layerName
            EPSG = "&CRS="+self.crc

            urlWithParams = url + getFeatureRequest + layer + EPSG
            return  urlWithParams    

        
        
