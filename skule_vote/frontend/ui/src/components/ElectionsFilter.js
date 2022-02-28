import React from "react";
import { styled } from "@mui/system";
import Paper from "@mui/material/Paper";
import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";
import ClearIcon from "@mui/icons-material/Clear";
import IconButton from "@mui/material/IconButton";
import Drawer from "@mui/material/Drawer";
import Divider from "@mui/material/Divider";
import Box from "@mui/material/Box";
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
    width: 250,
  },
  [theme.breakpoints.down("sm")]: {
    paddingTop: 0,
    marginRight: 0,
  },
}));

const FilterItem = styled(Button, {
  shouldForwardProp: (propName) => propName !== "active",
})(({ theme, active }) => ({
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
}) => (
  <Drawer anchor="left" open={drawerOpen} onClose={toggleDrawer}>
    <Box sx={{ display: "flex", justifyContent: "flex-end", m: "4px" }}>
      <IconButton
        data-testid="drawerClose"
        onClick={toggleDrawer}
        role="close"
        size="large"
      >
        <ClearIcon />
      </IconButton>
    </Box>
    <ElectionsFilter
      filterCategory={filterCategory}
      setAndCloseFilter={setAndCloseFilter}
    />
  </Drawer>
);

const ElectionsFilter = ({ filterCategory, setAndCloseFilter }) => {
  return (
    <ElectionsFilterPaper elevation={0}>
      <Typography variant="h2">Filter</Typography>
      <Divider />
      {Object.values(listOfCategories).map((category, i) => (
        <FilterItem
          active={filterCategory === category}
          key={i}
          onClick={() => setAndCloseFilter(category)}
          variant="filter"
          fullWidth
        >
          <Typography variant="body1">{category}</Typography>
        </FilterItem>
      ))}
    </ElectionsFilterPaper>
  );
};

export default ElectionsFilter;
