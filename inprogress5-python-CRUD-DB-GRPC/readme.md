# for future naufal

## updating proto file

this implementation is all about grpc . to recreate the protobuff user this comment 

```
python -m grpc_tools.protoc -I. --python_out=. --pyi_out=. --grpc_python_out=. books.proto

```

## running the server on changes

i also add hupper so each time the file have adjustment it's automaticly rerun the server 

```
hupper -m books_se