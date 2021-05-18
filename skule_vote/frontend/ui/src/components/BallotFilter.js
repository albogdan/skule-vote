import React from "react";
import styled from "styled-components";
import Paper from "@material-ui/core/Paper";
import Button from "@material-ui/core/Button";
import Typography from "@material-ui/core/Typography";
import { useTheme } from "@material-ui/core/styles";
import Divider from "@material-ui/core/Divider";
import { listOfCategories } from "pages/ElectionPage";
import { responsive } from "assets/breakpoints";

const BallotFilterPaper = styled(Paper)`
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
`;

const FilterItem = styled(Button)`
  padding: 12px 24px;
  justify-content: flex-start;
  border-radius: 0;
  text-transform: capitalize;
  background-color: ${(props) =>
    props.active && (props.isDark ? props.palette.primary.main : "#DDECF6")};
`;

const FilterItemWrapper = styled.div`
  display: flex;
  flex-direction: column;
  > button {
    &:hover {
      background-color: ${(props) =>
        props.isDark ? props.palette.primary.main : "#DDECF6"};
    }
  }
`;

const BallotFilter = ({ filterCategory, setFilterCategory }) => {
  const theme = useTheme();
  const isDark = theme.palette.type === "dark";

  return (
    <BallotFilterPaper>
      <Typography variant="h2">Filter</Typography>
      <Divider />
      <FilterItemWrapper palette={theme.palette} isDark={isDark}>
        {listOfCategories.map((category, i) => (
          <FilterItem
            palette={theme.palette}
            active={filterCategory === category}
            isDark={isDark}
            key={i}
            onClick={() => setFilterCategory(category)}
          >
            <Typography variant="body1">{category}</Typography>
          </FilterItem>
        ))}
      </FilterItemWrapper>
    </BallotFilterPaper>
  );
};

export default BallotFilter;
