import React from "react";
import styled from "styled-components";
import Paper from "@mui/material/Paper";
import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";
import ClearIcon from "@mui/icons-material/Clear";
import IconButton from "@mui/material/IconButton";
import Drawer from "@mui/material/Drawer";
import { useTheme } from "@mui/material/styles";
import Divider from "@mui/material/Divider";
import Box from "@mui/material/Box";
import { listOfCategories } from "pages/ElectionPage";
import { responsive } from "assets/breakpoints";

const ElectionsFilterPaper = styled(Paper)`
  display: flex;
  flex-direction: column;
  width: 275px;
  padding: 24px 0;
  margin-right: 64px;
  box-shadow: none;
  h2 {
    margin-left: 24px;
    font-weight: 400;
  }
  hr {
    margin: 16px 0;
  }
  @media ${responsive.mdDown} {
    margin-right: 16px;
    width: 250px;
  }
  @media ${responsive.smDown} {
    padding-top: 0;
    margin-right: 0;
    background-color: transparent !important;
    box-shadow: none !important;
    background-image: none !important;
  }
`;

const FilterItem = styled(Button)`
  background-color: ${(props) =>
    props.$active &&
    (props.$isDark ? props.$palette.primary.main : "#DDECF6")} !important;
  &:hover {
    background-color: ${(props) =>
      props.$isDark ? props.$palette.primary.main : "#DDECF6"} !important;
  }
`;

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
  const theme = useTheme();
  const isDark = theme.palette.mode === "dark";

  return (
    <ElectionsFilterPaper elevation={0}>
      <Typography variant="h2">Filter</Typography>
      <Divider />
      {Object.values(listOfCategories).map((category, i) => (
        <FilterItem
          $palette={theme.palette}
          $active={filterCategory === category}
          $isDark={isDark}
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
