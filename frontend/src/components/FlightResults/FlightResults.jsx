import React from "react";
import { Spin, Empty, Alert, Pagination, Select } from "antd";
import PropTypes from "prop-types";
import ItineraryCard from "../ItineraryCard/ItineraryCard";
import styles from "./FlightResults.module.scss";

const PAGE_SIZE_OPTIONS = [5, 10, 20, 50];

const FlightResults = ({
  loading,
  error,
  itineraries,
  totalCount,
  currentPage,
  pageSize,
  onPageChange,
  onPageSizeChange,
}) => {
  if (loading) {
    return (
      <div className={styles.centered}>
        <Spin size="large" tip="Searching flights..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.errorWrapper}>
        <Alert
          type="error"
          showIcon
          message="Search failed"
          description={error}
          className={styles.alert}
        />
      </div>
    );
  }

  if (!itineraries || itineraries.length === 0) {
    return (
      <Empty
        className={styles.centered}
        description="No itineraries found. Try different airports or date."
        image={Empty.PRESENTED_IMAGE_SIMPLE}
      />
    );
  }

  const total = totalCount ?? itineraries.length;
  const pageNumber = currentPage ?? 1;
  const size = pageSize ?? 10;
  const start = (pageNumber - 1) * size;
  const showRange = total > size;

  return (
    <div className={styles.list}>
      <div className={styles.titleRow}>
        <h3 className={styles.title}>
          {total} option(s) found
          {showRange && (
            <span className={styles.pageInfo}>
              {" "}
              (showing {start + 1}–{start + itineraries.length})
            </span>
          )}
        </h3>
        <div className={styles.pageSizeSelect}>
          <span className={styles.pageSizeLabel}>Per page:</span>
          <Select
            value={size}
            options={PAGE_SIZE_OPTIONS.map((n) => ({ label: n, value: n }))}
            onChange={onPageSizeChange}
            style={{ width: 72 }}
          />
        </div>
      </div>
      <div className={styles.scrollable}>
        {itineraries.map((it, i) => (
          <ItineraryCard key={start + i} itinerary={it} index={start + i} />
        ))}
      </div>
      {total > size && (
        <div className={styles.pagination}>
          <Pagination
            current={pageNumber}
            total={total}
            pageSize={size}
            onChange={onPageChange}
            showSizeChanger={false}
            showTotal={(t) => `${t} options`}
          />
        </div>
      )}
    </div>
  );
};

FlightResults.propTypes = {
  loading: PropTypes.bool,
  error: PropTypes.string,
  itineraries: PropTypes.arrayOf(PropTypes.object),
  totalCount: PropTypes.number,
  currentPage: PropTypes.number,
  pageSize: PropTypes.number,
  onPageChange: PropTypes.func,
  onPageSizeChange: PropTypes.func,
};

FlightResults.defaultProps = {
  loading: false,
  error: null,
  itineraries: null,
  totalCount: null,
  currentPage: 1,
  pageSize: 10,
  onPageChange: () => {},
  onPageSizeChange: () => {},
};

export default FlightResults;
