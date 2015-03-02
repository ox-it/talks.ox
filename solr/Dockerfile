FROM makuk66/docker-solr
MAINTAINER Micah Martin <micahlmartin@gmail.com>

ADD ./talks/conf/schema.xml /opt/solr/example/solr/collection1/conf/schema.xml
ADD ./talks/conf/solrconfig.xml /opt/solr/example/solr/collection1/conf/solrconfig.xml
ADD ./talks/conf/stopwords.txt /opt/solr/example/solr/collection1/conf/stopwords.txt
ADD ./talks/conf/lang /opt/solr/example/solr/collection1/conf/lang/

EXPOSE 8983
CMD ["/bin/bash", "-c", "cd /opt/solr/example; java -jar start.jar"]

