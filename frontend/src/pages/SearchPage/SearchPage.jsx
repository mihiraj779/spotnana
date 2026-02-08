import React, { useState } from "react";
import { Layout } from "antd";
import { toast } from "react-toastify";
import Header from "../../components/Header/Header";
import SearchForm from "../../components/SearchForm/SearchForm";
import FlightResults from "../../components/FlightResults/FlightResults";
import { searchFlights } from "../../services/flightSearchService";
import styles from "./SearchPage.module.scss";

const { Content } = Layout;

const DEFAULT_PAGE_SIZE = 10;

const SearchPage = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [itineraries, setItineraries] = useState(null);
  const [totalCount, setTotalCount] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [lastSearchParams, setLastSearchParams] = useState(null);
  const [pageSize, setPageSize] = useState(DEFAULT_PAGE_SIZE);

  const runSearch = async (params, pageNumber = 1, size = pageSize) => {
    const apiParams = { ...params, page_number: pageNumber, page_size: size };
    const data = await searchFlights(apiParams);
    setItineraries(data.itineraries || []);
    setTotalCount(data.total_count ?? 0);
    setCurrentPage(pageNumber);
    return data;
  };

  const handleSearch = async (params) => {
    if (params.origin === params.destination) {
      toast.error("Origin and destination must be different");
      setError("Origin and destination must be different");
      setItineraries(null);
      setTotalCount(null);
      return;
    }
    setError(null);
    setItineraries(null);
    setTotalCount(null);
    setLastSearchParams({
      origin: params.origin,
      destination: params.destination,
      date: params.date,
    });
    setLoading(true);
    try {
      const data = await runSearch(params, 1, pageSize);
      if (!data.itineraries?.length) {
        toast.info("No itineraries found");
      }
    } catch (err) {
      const message = err.message || "Search failed";
      setError(message);
      toast.error(message);
      setItineraries(null);
      setTotalCount(null);
    } finally {
      setLoading(false);
    }
  };

  const handlePageChange = (pageNum) => {
    if (!lastSearchParams) return;
    setLoading(true);
    runSearch(lastSearchParams, pageNum, pageSize)
      .finally(() => setLoading(false))
      .catch((err) => {
        setError(err.message || "Search failed");
        toast.error(err.message);
      });
  };

  const handlePageSizeChange = (size) => {
    setPageSize(size);
    if (!lastSearchParams) return;
    setLoading(true);
    runSearch(lastSearchParams, 1, size)
      .finally(() => setLoading(false))
      .catch((err) => {
        setError(err.message || "Search failed");
        toast.error(err.message);
      });
  };

  return (
    <Layout className={styles.layout}>
      <Header />
      <Content className={styles.content}>
        <div className={styles.container}>
          <div className={styles.searchSection}>
            <SearchForm onSearch={handleSearch} loading={loading} />
          </div>
          <FlightResults
            loading={loading}
            error={error}
            itineraries={itineraries}
            totalCount={totalCount}
            currentPage={currentPage}
            pageSize={pageSize}
            onPageChange={handlePageChange}
            onPageSizeChange={handlePageSizeChange}
          />
        </div>
      </Content>
    </Layout>
  );
};

export default SearchPage;
