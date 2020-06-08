from builder.Builder import Builder

# source = str(input("Input source file: "))
# destination = str(input("Input destination file: "))
source = "builder/products.json"
destination = "query/result.ttl"
builder = Builder(source, destination, ["varian"])
builder.buildKG()