from memory import ShaktiMemory

m = ShaktiMemory()
m.add("user", "Hello memory")
m.add("assistant", "I remember you")

print(m.get_recent())
