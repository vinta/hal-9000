if which java > /dev/null; then
  export JAVA_HOME="$(/usr/libexec/java_home -v 1.8)"
  export PATH="$JAVA_HOME/bin:$PATH"
fi

export PATH="/usr/local/opt/scala@2.12/bin:$PATH"

export SPARK_HOME="/usr/local/share/apache-spark/spark-2.4.3"
export PATH="$SPARK_HOME/bin:$PATH"
export PYTHONPATH="$SPARK_HOME/python:$PYTHONPATH"
