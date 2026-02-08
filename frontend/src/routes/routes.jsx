import React from "react";
import { createBrowserRouter } from "react-router-dom";
import SearchPage from "../pages/SearchPage/SearchPage";

export const routes = [
  {
    path: "/",
    element: <SearchPage />,
  },
  {
    path: "*",
    element: <SearchPage />,
  },
];

export const router = createBrowserRouter(routes);
