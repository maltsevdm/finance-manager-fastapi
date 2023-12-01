import React, {useEffect, useState} from "react";
import './iconList.css';
import {sendGet} from '../../utils.js';
import {url_icon} from "../../config.js";

const IconList = ({iconList}) => {
    const [active, setActive] = useState(false)

    function changeState ({target}) {
        setActive(active ? false : true)
        target.className = active ? "cat-icon active" : "cat-icon"
    }

    return (
        <div className="icon-list">
            {iconList.map(icon_name => 
                <img 
                src={url_icon + icon_name} 
                className="cat-icon"
                onClick={changeState}
                />)}
        </div>
    )
};

export default IconList;