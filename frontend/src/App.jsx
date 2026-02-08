import React from "react";
import { RouterProvider } from "react-router-dom";
import { ConfigProvider } from "antd";
import { ToastContainer } from "react-toastify";
import { router } from "./routes/routes";
import "react-toastify/dist/ReactToastify.css";

const App = () => (
  <ConfigProvider
    theme={{
      token: {
        colorPrimary: "#0a6ebd",
        borderRadius: 6,
      },
    }}
  >
    <ToastContainer position="top-right" autoClose={4000} />
    <RouterProvider router={router} />
  </ConfigProvider>
);

export default App;
