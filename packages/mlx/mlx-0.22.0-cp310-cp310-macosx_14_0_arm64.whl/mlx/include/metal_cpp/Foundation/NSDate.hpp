//-------------------------------------------------------------------------------------------------------------------------------------------------------------
//
// Foundation/NSDate.hpp
//
// Copyright 2020-2024 Apple Inc.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//
//-------------------------------------------------------------------------------------------------------------------------------------------------------------


#pragma once

//-------------------------------------------------------------------------------------------------------------------------------------------------------------

#include "NSDefines.hpp"
#include "NSObject.hpp"
#include "NSPrivate.hpp"
#include "NSTypes.hpp"

//-------------------------------------------------------------------------------------------------------------------------------------------------------------

namespace NS
{

using TimeInterval = double;

class Date : public Copying<Date>
{
public:
    static Date* dateWithTimeIntervalSinceNow(TimeInterval secs);
};

} // NS

//-------------------------------------------------------------------------------------------------------------------------------------------------------------

_NS_INLINE NS::Date* NS::Date::dateWithTimeIntervalSinceNow(NS::TimeInterval secs)
{
    return NS::Object::sendMessage<NS::Date*>(_NS_PRIVATE_CLS(NSDate), _NS_PRIVATE_SEL(dateWithTimeIntervalSinceNow_), secs);
}

//-------------------------------------------------------------------------------------------------------------------------------------------------------------