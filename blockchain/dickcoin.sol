pragma solidity ^0.4.11;

contract ICODickcoin {
    
    uint public maximumDicks = 10000000;
    uint public xvideosToDicks = 10;
    uint public dicksSucked = 0;
    
    mapping(address => uint) equityDicks;
    mapping(address => uint) equityXvideosCredits;
    
    modifier canBuy(uint xvideosCredits) {
        require(xvideosCredits * xvideosToDicks + dicksSucked <= maximumDicks);
        _;
    }
    
    function dicksEquity(address investor) external constant returns (uint) {
        return equityDicks[investor];
    }
    
    function xvideosCreditsEquity(address investor) external constant returns (uint) {
        return equityXvideosCredits[investor];
    }    
    
    function buy(address investor, uint xvideosCredits) external canBuy(xvideosCredits) {
        uint dicksToSuck = xvideosCredits * xvideosToDicks;
        equityDicks[investor] += dicksToSuck;
        equityXvideosCredits[investor] = equityDicks[investor] / xvideosToDicks;
        dicksSucked += dicksToSuck;
    }
    
    function sell(address investor, uint dicksToSpit) external {
        equityDicks[investor] -= dicksToSpit;
        equityXvideosCredits[investor] = equityDicks[investor] / xvideosToDicks;
        dicksSucked -= dicksToSpit;
    }
    
}