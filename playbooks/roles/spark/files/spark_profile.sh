if which java > /dev/null; then
  export JAVA_HOME="$(/usr/libexec/java_home -v11)"
  export PATH="$JAVA_HOME/bin:$PATH"
fi

export SPARK_HOME="/usr/local/share/apache-spark/spark-3.0.0"
export PATH="$SPARK_HOME/bin:$PATH"
export PYTHONPATH="$SPARK_HOME/python:$PYTHONPATH"
