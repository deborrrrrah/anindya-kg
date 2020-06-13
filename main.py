from builder.Builder import Builder

# source = str(input("Input source file: "))
# destination = str(input("Input destination file: "))
source = "builder/products-v2.json"
destination = "query/result-v2.ttl"
builder = Builder(source, destination, ["varian"])
builder.buildKG()