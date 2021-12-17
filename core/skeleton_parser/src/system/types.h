namespace seamless
{
    using XYCoordinate = std::pair<float, float>;
    using PersonKeypoints = std::vector<XYCoordinate>;
    using PeopleKeypoints = std::pair<int, std::vector<PersonKeypoints>>;
}