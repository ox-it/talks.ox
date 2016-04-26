FROM makuk66/docker-solr:4.10.4

ADD ./talks/conf/schema.xml /opt/solr/example/solr/collection1/conf/schema.xml
ADD ./talks/conf/solrconfig.xml /opt/solr/example/solr/collection1/conf/solrconfig.xml
ADD ./talks/conf/stopwords.txt /opt/solr/example/solr/collection1/conf/stopwords.txt
ADD ./talks/conf/lang /opt/solr/example/solr/collection1/conf/lang/

# CMD ["/bin/bash", "-c", "cd /opt/solr/example; java -jar start.jar"]

EXPOSE 8983
