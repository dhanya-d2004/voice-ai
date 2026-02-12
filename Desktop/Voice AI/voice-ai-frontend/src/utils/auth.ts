export const signupUser = (email: string, password: string) => {
  const users = JSON.parse(localStorage.getItem("users") || "[]");

  const userExists = users.find((u: any) => u.email === email);
  if (userExists) {
    return { success: false, message: "User already exists" };
  }

  users.push({ email, password });
  localStorage.setItem("users", JSON.stringify(users));
  return { success: true };
};

export const loginUser = (email: string, password: string) => {
  const users = JSON.parse(localStorage.getItem("users") || "[]");

  const user = users.find(
    (u: any) => u.email === email && u.password === password
  );

  if (!user) {
    return { success: false, message: "Invalid credentials" };
  }

  localStorage.setItem("loggedIn", "true");
  return { success: true };
};

export const logoutUser = () => {
  localStorage.removeItem("loggedIn");
};
