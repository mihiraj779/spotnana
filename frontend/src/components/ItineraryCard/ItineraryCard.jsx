import React from "react";
import { Card } from "antd";
import PropTypes from "prop-types";
import dayjs from "dayjs";
import styles from "./ItineraryCard.module.scss";

const formatDuration = (minutes) => {
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return m > 0 ? `${h}h ${m}m` : `${h}h`;
};

/**
 * Format departure/arrival for display. Accepts full ISO (e.g. 2024-03-17T08:00:00).
 * Always shows date and time (e.g. Mar 15, 10:00).
 */
const formatSegmentTime = (isoStr) => {
  if (!isoStr) return "";
  const dt = dayjs(isoStr);
  if (!dt.isValid()) return String(isoStr);
  return dt.format("MMM D, HH:mm");
};

const ItineraryCard = ({ itinerary, index }) => {
  const { segments, layovers, totalDurationMinutes, totalPrice } = itinerary;

  return (
    <Card className={styles.card} size="small">
      <div className={styles.header}>
        <span className={styles.badge}>Option {index + 1}</span>
        <span className={styles.duration}>
          {formatDuration(totalDurationMinutes)} total
        </span>
        <span className={styles.price}>${Number(totalPrice).toFixed(2)}</span>
      </div>
      <div className={styles.segments}>
        {segments.map((seg, i) => (
          <React.Fragment key={i}>
            <div className={styles.segment}>
              <span className={styles.flightNum}>{seg.flightNumber}</span>
              <span className={styles.route}>
                {seg.origin} → {seg.destination}
              </span>
              <span className={styles.time}>
                {formatSegmentTime(seg.departureTime)} –{" "}
                {formatSegmentTime(seg.arrivalTime)}
              </span>
              <span className={styles.segPrice}>
                ${Number(seg.price).toFixed(2)}
              </span>
            </div>
            {layovers[i] && (
              <div className={styles.layover}>
                <span className={styles.layoverPill}>
                  {layovers[i].airport} · {layovers[i].durationMinutes} min
                </span>
              </div>
            )}
          </React.Fragment>
        ))}
      </div>
    </Card>
  );
};

ItineraryCard.propTypes = {
  itinerary: PropTypes.shape({
    segments: PropTypes.arrayOf(
      PropTypes.shape({
        flightNumber: PropTypes.string,
        origin: PropTypes.string,
        destination: PropTypes.string,
        departureTime: PropTypes.string,
        arrivalTime: PropTypes.string,
        price: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
      }),
    ),
    layovers: PropTypes.arrayOf(
      PropTypes.shape({
        airport: PropTypes.string,
        durationMinutes: PropTypes.number,
      }),
    ),
    totalDurationMinutes: PropTypes.number,
    totalPrice: PropTypes.number,
  }).isRequired,
  index: PropTypes.number.isRequired,
};

export default ItineraryCard;
