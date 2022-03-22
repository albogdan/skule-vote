import React, { useEffect, useState } from "react";
import { styled } from "@mui/system";
import Paper from "@mui/material/Paper";
import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";
import ClearIcon from "@mui/icons-material/Clear";
import IconButton from "@mui/material/IconButton";
import Drawer from "@mui/material/Drawer";
import Divider from "@mui/material/Divider";
import Stack from "@mui/material/Stack";
import Chip from "@mui/material/Chip";
import { listOfCategories } from "pages/ElectionPage";

const ElectionsFilterPaper = styled(Paper)(({ theme }) => ({
  display: "flex",
  flexDirection: "column",
  width: 275,
  padding: "24px 0",
  marginRight: 64,
  boxShadow: "none",
  backgroundImage: "none",
  h2: {
    marginLeft: 24,
    fontWeight: 400,
  },
  hr: {
    margin: "16px 0",
  },
  [theme.breakpoints.down("md")]: {
    marginRight: 16,
    width: 260,
  },
  [theme.breakpoints.down("sm")]: {
    paddingTop: 0,
    marginRight: 0,
  },
}));

const FilterItem = styled(Button, {
  shouldForwardProp: (propName) => propName !== "active",
})(({ theme, active }) => ({
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  backgroundColor:
    active &&
    (theme.palette.mode === "dark" ? theme.palette.primary.main : "#DDECF6"),
  ":hover": {
    backgroundColor:
      theme.palette.mode === "dark" ? theme.palette.primary.main : "#DDECF6",
  },
}));

export const ElectionsFilterDrawer = ({
  drawerOpen,
  toggleDrawer,
  filterCategory,
  setAndCloseFilter,
  eligibleElections,
}) => (
  <Drawer anchor="left" open={drawerOpen} onClose={toggleDrawer}>
    <Stack direction="row" justifyContent="flex-end" m={0.5}>
      <IconButton
        data-testid="drawerClose"
        onClick={toggleDrawer}
        role="close"
        size="large"
      >
        <ClearIcon />
      </IconButton>
    </Stack>
    <ElectionsFilter
      filterCategory={filterCategory}
      setAndCloseFilter={setAndCloseFilter}
      eligibleElections={eligibleElections}
    />
  </Drawer>
);

const ElectionsFilter = ({
  eligibleElections,
  filterCategory,
  setAndCloseFilter,
}) => {
  const [electionsCount, setElectionsCount] = useState({});

  useEffect(() => {
    const cnt = Object.values(eligibleElections ?? {}).reduce(
      (prev, curr) => {
        if (curr.category in prev) {
          prev[curr.category]++;
        } else {
          prev[curr.category] = 1;
        }
        return prev;
      },
      { all: Object.values(eligibleElections ?? {}).length }
    );
    setElectionsCount(cnt);
  }, [eligibleElections]);

  return (
    <ElectionsFilterPaper elevation={0}>
      <Typography variant="h2">Filter</Typography>
      <Divider />
      {Object.keys(listOfCategories).map((category, i) => (
        <FilterItem
          active={filterCategory === listOfCategories[category]}
          key={i}
          onClick={() => setAndCloseFilter(listOfCategories[category])}
          variant="filter"
          fullWidth
        >
          <Typography variant="body1">{listOfCategories[category]}</Typography>
          <Chip label={electionsCount[category] ?? "0"} />
        </FilterItem>
      ))}
    </ElectionsFilterPaper>
  );
};

export default ElectionsFilter;
